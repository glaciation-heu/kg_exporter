from typing import Any, Dict, List, Optional, Tuple, TypeAlias

from jsonpath_ng.ext import parse

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.resource_snapshot_index import ResourceSnapshotIndex
from app.core.slice_strategy import SliceStrategy
from app.core.types import KGSliceId, MetricSnapshot, SliceInputs

ReferenceKind: TypeAlias = str


# TODO rename
class SliceForNodeStrategy(SliceStrategy):
    node_port: int

    def __init__(self, node_port: int):
        self.node_port = node_port

    def get_slices(
        self, resources: ResourceSnapshot, metrics: MetricSnapshot
    ) -> Dict[KGSliceId, SliceInputs]:
        result: Dict[KGSliceId, SliceInputs] = dict()
        index = ResourceSnapshotIndex.build(resources)
        for node in resources.nodes:
            slice_id, inputs = self.split_node(node, index, resources, metrics)
            result[slice_id] = inputs

        return result

    def split_node(
        self,
        node: Dict[str, Any],
        index: ResourceSnapshotIndex,
        src_resources: ResourceSnapshot,
        src_metrics: MetricSnapshot,
    ) -> Tuple[KGSliceId, SliceInputs]:
        node_hostname = self.get_resource_name(node)
        slice_id = KGSliceId(node_hostname, self.node_port)

        slice_resources = ResourceSnapshot(cluster=src_resources.cluster, nodes=[node])
        slice_metrics = MetricSnapshot()
        self.add_workloads(node_hostname, index, slice_resources, src_resources)
        self.add_metrics(slice_resources, slice_metrics, src_metrics)

        return slice_id, SliceInputs(slice_resources, slice_metrics)

    def get_resource_name(self, resource: Dict[str, Any]) -> str:
        return resource["metadata"]["name"]  # type: ignore

    def add_workloads(
        self,
        node_hostname: str,
        index: ResourceSnapshotIndex,
        slice_resources: ResourceSnapshot,
        src_resources: ResourceSnapshot,
    ) -> None:
        for pod in src_resources.pods:
            hostname = self.get_pod_hostname(pod)
            if not hostname or hostname != node_hostname:
                continue
            slice_resources.pods.append(pod)
            self.add_parent_resources(pod, index, slice_resources, src_resources)

    def add_parent_resources(
        self,
        resource: Dict[str, Any],
        index: ResourceSnapshotIndex,
        slice_resources: ResourceSnapshot,
        src_resources: ResourceSnapshot,
    ) -> None:
        for parent_kind, parent_identity in self.get_owner_references(resource):
            src_found_resource = index.get_by(parent_kind, parent_identity)
            if src_found_resource:
                slice_resources.add_resources_by_kind(parent_kind, [src_found_resource])
                self.add_parent_resources(
                    src_found_resource, index, slice_resources, src_resources
                )

    def get_owner_references(
        self, resource: Dict[str, Any]
    ) -> List[Tuple[ReferenceKind, str]]:
        references_matches = resource["metadata"].get("ownerReferences") or []
        if len(references_matches) == 0:
            return []
        return [
            self.get_reference_id(reference_match)
            for reference_match in references_matches
        ]

    def get_pod_hostname(self, pod: Dict[str, Any]) -> Optional[str]:
        return pod.get("spec").get("nodeName")  # type: ignore

    def get_reference_id(self, reference: Dict[str, Any]) -> Tuple[str, str]:
        return reference["kind"], reference["name"]

    def add_metrics(
        self,
        slice_resources: ResourceSnapshot,
        slice_metrics: MetricSnapshot,
        src_metrics: MetricSnapshot,
    ) -> None:
        for node in slice_resources.nodes:
            node_name = self.get_resource_name(node)
            metrics = src_metrics.get_node_metrics_by_resource(node_name)
            slice_metrics.node_metrics.extend(metrics)

        for pod in slice_resources.pods:
            pod_name = self.get_pod_name(pod)
            metrics = src_metrics.get_pod_metrics_by_resource(pod_name)
            slice_metrics.pod_metrics.extend(metrics)

    def get_pod_name(self, resource: Dict[str, Any]) -> str:
        name = parse("$.metadata.name").find(resource)[0].value
        namespace = parse("$.metadata.namespace").find(resource)[0].value
        return f"{namespace}.{name}"
