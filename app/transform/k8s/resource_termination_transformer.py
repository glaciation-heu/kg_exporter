from typing import Any, Dict, List, Set

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.kg.kg_snapshot import KGSnapshot
from app.kg.graph import Graph
from app.kg.iri import IRI
from app.transform.transformation_context import TransformationContext
from app.transform.transformer_base import TransformerBase
from app.transform.upper_ontology_base import UpperOntologyBase


class ResourceTerminationTransformer(UpperOntologyBase):
    POD_TERMINATED_STATES: Set[str] = {"Succeeded", "Failed", "Unknown"}

    resources: ResourceSnapshot
    existing_metadata: KGSnapshot

    def __init__(
        self,
        resources: ResourceSnapshot,
        existing_metadata: KGSnapshot,
        sink: Graph,
    ):
        UpperOntologyBase.__init__(self, sink)
        self.resources = resources
        self.existing_metadata = existing_metadata

    def transform(self, context: TransformationContext) -> None:
        now_date = context.get_timestamp_as_str(self.DATETIME_FORMAT)
        self.terminate_nodes(now_date)
        self.terminate_pods(now_date)
        self.terminate_containers(now_date)

    def terminate_nodes(self, now_date: str) -> None:
        ids_from_resources = {self.get_node_id(node) for node in self.resources.nodes}
        for node_status in self.existing_metadata.nodes:
            node_id = IRI(
                TransformerBase.CLUSTER_PREFIX, node_status.identifier.get_value()
            )
            if node_id not in ids_from_resources and node_status.status != "Unknown":
                self.add_work_producing_resource(node_id, "KubernetesWorkerNode")
                status_id = node_id.dot("Status")
                self.add_status(status_id, "Unknown", None, now_date)
                self.sink.add_relation(node_id, self.HAS_STATUS, status_id)

    def get_node_id(self, node_resource: Dict[str, Any]) -> IRI:
        name = node_resource["metadata"]["name"]
        resource_id = IRI(TransformerBase.CLUSTER_PREFIX, name)
        return resource_id

    def terminate_pods(self, now_date: str) -> None:
        ids_from_resources = {self.get_pod_id(pod) for pod in self.resources.pods}
        for pod_status in self.existing_metadata.pods:
            pod_id = IRI(
                TransformerBase.CLUSTER_PREFIX, pod_status.identifier.get_value()
            )
            if pod_id not in ids_from_resources and not (
                pod_status.status in self.POD_TERMINATED_STATES
            ):
                status_id = pod_id.dot("Status")
                self.add_work_producing_resource(pod_id, "Pod")
                self.add_status(status_id, "Unknown", None, now_date)
                self.sink.add_relation(pod_id, self.HAS_STATUS, status_id)

    def get_pod_id(self, pod_resource: Dict[str, Any]) -> IRI:
        name = pod_resource["metadata"]["name"]
        namespace = pod_resource["metadata"]["namespace"]
        return IRI(TransformerBase.CLUSTER_PREFIX, namespace).dot(name)

    def terminate_containers(self, now_date: str) -> None:
        pod_containers = {
            self.get_pod_id(pod): self.get_container_ids(pod)
            for pod in self.resources.pods
        }
        all_container_ids = {
            container_id
            for _, container_ids in pod_containers.items()
            for container_id in container_ids
        }
        for container_status in self.existing_metadata.containers:
            container_id = IRI(
                TransformerBase.CLUSTER_PREFIX, container_status.identifier.get_value()
            )
            if (
                container_id not in all_container_ids
                and container_status.status != "terminated"
            ):
                status_id = container_id.dot("Status")
                self.add_work_producing_resource(container_id, "Container")
                self.add_status(status_id, "terminated", None, now_date)
                self.sink.add_relation(container_id, self.HAS_STATUS, status_id)

    def get_container_ids(self, pod: Dict[str, Any]) -> Set[IRI]:
        container_ids: Set[IRI] = self.get_container_ids_from_status(
            pod, ["status", "containerStatuses"]
        )
        init_container_ids: Set[IRI] = self.get_container_ids_from_status(
            pod, ["status", "initContainerStatuses"]
        )
        return container_ids | init_container_ids

    def get_container_ids_from_status(
        self, pod: Dict[str, Any], jsonpath: List[str]
    ) -> Set[IRI]:
        pod_id = self.get_pod_id(pod)
        container_status_matches = TransformerBase.get_opt_list(pod, jsonpath) or []
        container_ids: Set[IRI] = set()
        for container in container_status_matches:
            k8s_container_name = container.get("name") or "undefined"
            container_id = pod_id.dot(k8s_container_name)
            container_ids.add(container_id)
        return container_ids
