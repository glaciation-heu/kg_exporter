from typing import Any, Dict, List, Optional, Tuple

import re

from app.k8s_transform.transformation_context import TransformationContext
from app.k8s_transform.transformer_base import TransformerBase
from app.k8s_transform.upper_ontology_base import UpperOntologyBase
from app.kg.graph import Graph
from app.kg.iri import IRI
from app.kg.literal import Literal


class PodToRDFTransformer(TransformerBase, UpperOntologyBase):
    def __init__(self, source: Dict[str, Any], sink: Graph):
        TransformerBase.__init__(self, source, sink)
        UpperOntologyBase.__init__(self, sink)

    def transform(self, _: TransformationContext) -> None:
        pod_id = self.get_pod_id()
        self.add_work_producing_resource(pod_id, "Pod")
        self.add_references(pod_id, "Pod")
        scheduler_name = (
            self.get_opt_str_value(["spec", "schedulerName"]) or "default-scheduler"
        )
        self.add_str_property(pod_id, self.HAS_NAME, "$.metadata.name")
        self.add_scheduler_reference(pod_id, scheduler_name)
        self.add_node_reference(pod_id)
        self.add_pod_status(pod_id)
        self.add_containers_resources(pod_id, scheduler_name)

    def add_scheduler_reference(self, resource_id: IRI, scheduler_name: str) -> None:
        scheduler_id = IRI(self.GLACIATION_PREFIX, scheduler_name)
        self.add_scheduler(scheduler_id, None)
        self.sink.add_relation(scheduler_id, self.MANAGES, resource_id)

    def add_node_reference(self, pod_id: IRI) -> None:
        node_name = self.get_opt_str_value(["spec", "nodeName"])
        if node_name:
            node_id = IRI(self.CLUSTER_PREFIX, node_name)
            self.add_work_producing_resource(node_id, "KubernetesWorkerNode")
            self.sink.add_relation(pod_id, self.CONSUMES, node_id)

    def add_pod_status(self, pod_id: IRI) -> None:
        status_id = pod_id.dot("Status")
        start_time = self.get_opt_str_value(["status", "startTime"])
        status = self.get_opt_str_value(["status", "phase"])
        if status:
            self.add_status(status_id, status, start_time or "", None)

    def add_containers_resources(self, pod_id: IRI, scheduler_name: str) -> None:
        self.add_container_resources_by_query(
            pod_id, scheduler_name, ["status", "containerStatuses"]
        )
        self.add_container_resources_by_query(
            pod_id, scheduler_name, ["status", "initContainerStatuses"]
        )

    def add_container_resources_by_query(
        self, pod_id: IRI, scheduler_name: str, jsonpath: List[str]
    ) -> None:
        container_status_matches = self.get_opt_list(jsonpath) or []
        for container_match in container_status_matches:
            self.add_container_resource(pod_id, container_match, scheduler_name)

    def add_container_resource(
        self, pod_id: IRI, container: Dict[str, Any], scheduler_name: str
    ) -> None:
        k8s_container_id = container.get("containerID") or "undefined"
        k8s_container_name = container.get("name") or "undefined"
        container_id = pod_id.dot(k8s_container_name)
        self.add_work_producing_resource(container_id, "Container")
        self.add_scheduler_reference(container_id, scheduler_name)
        self.sink.add_property(
            container_id,
            self.HAS_CONTAINER_ID,
            Literal(k8s_container_id, Literal.TYPE_STRING),
        )
        self.sink.add_property(
            container_id,
            self.HAS_CONTAINER_NAME,
            Literal(k8s_container_name, Literal.TYPE_STRING),
        )
        state = container.get("state")
        if state:
            self.add_container_status(container_id, state)
        self.sink.add_relation(pod_id, self.HAS_SUBRESOURCE, container_id)

    def add_container_status(
        self, container_id: IRI, container_state: Dict[str, Any]
    ) -> None:
        status_id = container_id.dot("Status")
        state_struct, state_literal = self.get_state_struct(container_state)
        if state_literal and state_struct:
            start_time = state_struct.get("startedAt")
            end_time = state_struct.get("finishedAt")
            self.add_status(status_id, state_literal, start_time or "", end_time)

    def get_state_struct(
        self, state: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        possible_statues = ["waiting", "running", "terminated"]
        for status in possible_statues:
            status_struct = state.get(status)
            if status_struct:
                return status_struct, status
        return None, None

    def normalize_container_id(self, container_id: str) -> str:
        return re.sub("[:/]+", "-", container_id)
