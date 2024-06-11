from typing import Any, Dict, List, Optional, Tuple, TypeAlias

from jsonpath_ng.ext import parse

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.slice_strategy import SliceStrategy
from app.core.types import KGSliceId, MetricSnapshot, SliceInputs

ReferenceKind: TypeAlias = str


class SliceForNodeStrategy(SliceStrategy):
    node_port: int

    def __init__(self, node_port: int):
        self.node_port = node_port

    def get_slices(
        self, resources: ResourceSnapshot, metrics: MetricSnapshot
    ) -> Dict[KGSliceId, SliceInputs]:
        result: Dict[KGSliceId, SliceInputs] = dict()

        for node in resources.nodes:
            slice_id, inputs = self.split_node(node, resources, metrics)
            result[slice_id] = inputs

        return result

    def split_node(
        self,
        node: Dict[str, Any],
        src_resources: ResourceSnapshot,
        src_metrics: MetricSnapshot,
    ) -> Tuple[KGSliceId, SliceInputs]:
        node_hostname = self.get_resource_name(node)
        slice_id = KGSliceId(node_hostname, self.node_port)

        slice_resources = ResourceSnapshot(cluster=src_resources.cluster, nodes=[node])
        slice_metrics = MetricSnapshot()

        self.add_workloads(node_hostname, slice_resources, src_resources)
        self.add_metrics(slice_resources, slice_metrics, src_metrics)

        return slice_id, SliceInputs(slice_resources, slice_metrics)

    def get_resource_name(self, resource: Dict[str, Any]) -> str:
        for match in parse("$.metadata.name").find(resource):
            return str(match.value)
        raise Exception("Metadata does not contain name.")

    def add_workloads(
        self,
        node_hostname: str,
        slice_resources: ResourceSnapshot,
        src_resources: ResourceSnapshot,
    ) -> None:
        for pod in src_resources.pods:
            hostname = self.get_pod_hostname(pod)
            if not hostname or hostname != node_hostname:
                continue
            slice_resources.pods.append(pod)
            self.add_parent_resources(pod, slice_resources, src_resources)

    def add_parent_resources(
        self,
        resource: Dict[str, Any],
        slice_resources: ResourceSnapshot,
        src_resources: ResourceSnapshot,
    ) -> None:
        for parent_kind, parent_identity in self.get_owner_references(resource):
            src_found_resources = src_resources.find_resources_by_kind_and_identity(
                parent_kind, parent_identity
            )
            slice_resources.add_resources_by_kind(parent_kind, src_found_resources)
            for found_resource in src_found_resources:
                self.add_parent_resources(
                    found_resource, slice_resources, src_resources
                )

    def get_owner_references(
        self, resource: Dict[str, Any]
    ) -> List[Tuple[ReferenceKind, str]]:
        references_match = parse("$.metadata.ownerReferences").find(resource)
        if len(references_match) == 0:
            return []
        return [
            self.get_reference_id(reference_match)
            for reference_match in references_match[0].value
        ]

    def get_pod_hostname(self, pod: Dict[str, Any]) -> Optional[str]:
        for match in parse("$.spec.nodeName").find(pod):
            return str(match.value)
        return None

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
            pod_name = self.get_resource_name(pod)
            metrics = src_metrics.get_pod_metrics_by_resource(pod_name)
            slice_metrics.pod_metrics.extend(metrics)
