from typing import Any, Dict, Optional, Tuple

import re

from jsonpath_ng.ext import parse

from app.k8s_transform.transformer_base import TransformerBase
from app.kg.graph import Graph
from app.kg.iri import IRI
from app.kg.literal import Literal
from app.kg.types import RelationSet


class PodToRDFTransformer(TransformerBase):
    def __init__(self, source: Dict[str, Any], sink: Graph):
        super().__init__(source, sink)

    def transform(self) -> None:
        pod_id = self.get_pod_id()
        self.sink.add_meta_property(
            pod_id, Graph.RDF_TYPE_IRI, IRI(self.GLACIATION_PREFIX, "Pod")
        )
        self.write_collection(
            pod_id, IRI(self.GLACIATION_PREFIX, "has-label"), "$.metadata.labels"
        )
        self.write_collection(
            pod_id,
            IRI(self.GLACIATION_PREFIX, "has-annotation"),
            "$.metadata.annotations",
        )
        self.write_references(pod_id)
        self.write_node_id_reference(pod_id)
        self.write_tuple(
            pod_id, IRI(self.GLACIATION_PREFIX, "qos-class"), "$.status.qosClass"
        )
        self.write_tuple(
            pod_id, IRI(self.GLACIATION_PREFIX, "start-time"), "$.status.startTime"
        )
        self.write_tuple(
            pod_id, IRI(self.GLACIATION_PREFIX, "pod-phase"), "$.status.phase"
        )

        self.write_network(pod_id)

        self.write_containers(pod_id, "$.status.containerStatuses", "$.spec.containers")
        self.write_containers(
            pod_id, "$.status.initContainerStatuses", "$.spec.initContainers"
        )
        self.write_other_spec_properties(pod_id, "$.spec")

    def write_containers(
        self, pod_id: IRI, status_property: str, container_spec_property: str
    ) -> None:
        container_ids: RelationSet = set()

        container_status_matches = parse(status_property).find(self.source)
        if len(container_status_matches) == 0:
            return
        for container_match in container_status_matches[0].value:
            container_id = container_match.get("containerID")
            if not container_id:
                continue
            container_iri = IRI(
                self.CLUSTER_PREFIX, self.normalize_container_id(container_id)
            )
            name = container_match.get("name")
            restart_count = container_match.get("restartCount")
            container_ids.add(container_iri)
            self.sink.add_meta_property(
                container_iri,
                Graph.RDF_TYPE_IRI,
                IRI(self.GLACIATION_PREFIX, "Container"),
            )
            self.sink.add_property(
                container_iri,
                IRI(self.GLACIATION_PREFIX, "has-name"),
                Literal(self.escape(name), "str"),
            )
            self.sink.add_property(
                container_iri,
                IRI(self.GLACIATION_PREFIX, "restart-count"),
                Literal(str(restart_count), "str"),
            )
            state = container_match.get("state")
            if state:
                self.write_state(container_iri, state)

            self.write_resources(container_iri, container_spec_property, name)

        self.sink.add_relation_collection(
            pod_id, IRI(self.GLACIATION_PREFIX, "has-container"), container_ids
        )

    def normalize_container_id(self, container_id: str) -> str:
        return re.sub("[:/]+", "-", container_id)

    def write_resources(
        self, container_id: IRI, container_spec_property: str, container_name: str
    ) -> None:
        resource_spec_matches = parse(
            f"{container_spec_property}[?name='{container_name}'].resources"
        ).find(self.source)
        if len(resource_spec_matches) == 0:
            return
        resources = resource_spec_matches[0].value
        self.write_tuple_from(
            resources,
            container_id,
            IRI(self.GLACIATION_PREFIX, "requests-cpu"),
            "$.requests.cpu",
        )
        self.write_tuple_from(
            resources,
            container_id,
            IRI(self.GLACIATION_PREFIX, "requests-memory"),
            "$.requests.memory",
        )
        self.write_tuple_from(
            resources,
            container_id,
            IRI(self.GLACIATION_PREFIX, "limits-cpu"),
            "$.limits.cpu",
        )
        self.write_tuple_from(
            resources,
            container_id,
            IRI(self.GLACIATION_PREFIX, "limits-memory"),
            "$.limits.memory",
        )

    def write_other_spec_properties(
        self, container_id: IRI, container_spec_property: str
    ) -> None:
        spec_matches = parse(f"{container_spec_property}").find(self.source)
        if len(spec_matches) == 0:
            return
        self.write_tuple_from(
            spec_matches[0].value,
            container_id,
            IRI(self.GLACIATION_PREFIX, "is-scheduled-by"),
            "$.schedulerName",
        )

    def write_state(self, container_id: IRI, state: Any) -> None:
        state_struct, state_literal = self.get_state_struct(state)
        if state_literal:
            self.sink.add_property(
                container_id,
                IRI(self.GLACIATION_PREFIX, "state"),
                Literal(self.escape(state_literal), "str"),
            )
        if state_struct:
            self.write_tuple_from(
                state_struct,
                container_id,
                IRI(self.GLACIATION_PREFIX, "started-at"),
                "$.startedAt",
            )
            self.write_tuple_from(
                state_struct,
                container_id,
                IRI(self.GLACIATION_PREFIX, "finished-at"),
                "$.finishedAt",
            )
            self.write_tuple_from(
                state_struct,
                container_id,
                IRI(self.GLACIATION_PREFIX, "reason"),
                "$.reason",
            )

    def get_state_struct(
        self, state: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        possible_statues = ["waiting", "running", "terminated"]
        for status in possible_statues:
            status_struct = state.get(status)
            if status_struct:
                return status_struct, status
        return None, None

    def write_network(self, pod_id: IRI) -> None:
        self.write_tuple(
            pod_id, IRI(self.GLACIATION_PREFIX, "host-ip"), "$.status.hostIP"
        )
        self.write_tuple(
            pod_id, IRI(self.GLACIATION_PREFIX, "pod-ip"), "$.status.podIP"
        )

    def write_node_id_reference(self, pod_id: IRI) -> None:
        node_name_match = parse("$.spec.nodeName").find(self.source)
        if len(node_name_match) == 0:
            return
        for node_name in node_name_match:
            node_id = IRI(self.CLUSTER_PREFIX, node_name.value)
            self.sink.add_relation(
                pod_id, IRI(self.GLACIATION_PREFIX, "runs-on"), node_id
            )
            self.sink.add_meta_property(
                node_id, Graph.RDF_TYPE_IRI, IRI(self.GLACIATION_PREFIX, "Node")
            )
            self.sink.add_relation(
                node_id, IRI(self.GLACIATION_PREFIX, "has-pod"), pod_id
            )
