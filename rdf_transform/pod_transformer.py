
import json
from typing import Any, Dict, List, Optional, Tuple
from jsonpath_ng.ext import parse
from rdf_transform.transformer_base import TransformerBase
from rdf_transform.tuple_writer import TupleWriter
import re

class PodToRDFTransformer(TransformerBase):
    sink: TupleWriter

    def __init__(self, source: Dict[str, Any], sink: TupleWriter):
        super().__init__(source)
        self.sink = sink

    def transform(self) -> None:
        pod_id = self.get_pod_id()
        self.sink.add_tuple(pod_id, "rdf:type", ":Pod")
        self.write_collection(pod_id, ":has-label", '$.metadata.labels')
        self.write_collection(pod_id, ":has-annotation", '$.metadata.annotations')
        self.write_references(pod_id)
        self.write_node_id_reference(pod_id) 
        self.write_tuple(pod_id, ":qos-class", "$.status.qosClass")
        self.write_tuple(pod_id, ":start-time", "$.status.startTime")        
        self.write_tuple(pod_id, ":pod-phase", "$.status.phase")

        self.write_network(pod_id)

        self.write_containers(pod_id, "$.status.containerStatuses", "$.spec.containers")
        self.write_containers(pod_id, "$.status.initContainerStatuses", "$.spec.initContainers")

        self.sink.flush()

    def write_containers(self, pod_id: str, status_property: str, container_spec_property: str) -> None:
        container_ids = []
        
        container_status_matches = parse(status_property).find(self.source)
        if len(container_status_matches) == 0:
            return
        for container_match in container_status_matches[0].value:
            container_id = container_match.get("containerID")
            if not container_id:
                continue
            container_id = self.normalize_container_id(container_id)
            name = container_match.get("name")
            restart_count = container_match.get("restartCount")        
            container_ids.append(container_id)
            self.sink.add_tuple(container_id, "rdf:type", ":Container")
            self.sink.add_tuple(container_id, ":has-name", self.escape(name))
            self.sink.add_tuple(container_id, ":restart-count", str(restart_count))
            state = container_match.get("state")
            if state:
                self.write_state(container_id, state) 

            self.write_resources(container_id, container_spec_property, name)

        container_ids = " ".join(container_ids)
        self.sink.add_tuple(pod_id, ":has-container", f"({container_ids})")

    def normalize_container_id(self, container_id: str) -> str:
        container_id = re.sub("[:/]+", "-", container_id)
        return f":{container_id}"

    def write_resources(self, container_id: str, container_spec_property: str, container_name: str) -> None:
        resource_spec_matches = parse(f"{container_spec_property}[?name='{container_name}'].resources").find(self.source)
        if len(resource_spec_matches) == 0:
            return
        resources = resource_spec_matches[0].value
        self.write_tuple_from(resources, container_id, ":requests-cpu", "$.requests.cpu")
        self.write_tuple_from(resources, container_id, ":requests-memory", "$.requests.memory")
        self.write_tuple_from(resources, container_id, ":limits-cpu", "$.limits.cpu")
        self.write_tuple_from(resources, container_id, ":limits-memory", "$.limits.memory")

    def write_state(self, container_id: str, state: Any) -> None:        
        state_struct, state_literal = self.get_state_struct(state)
        if state_struct:
            self.sink.add_tuple(container_id, ":state", self.escape(state_literal))
            self.write_tuple_from(state_struct, container_id, ":started-at", "$.startedAt")
            self.write_tuple_from(state_struct, container_id, ":finished-at", "$.finishedAt")        
            self.write_tuple_from(state_struct, container_id, ":reason", "$.reason")        

    def get_state_struct(self, state: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        possible_statues = ["waiting", "running", "terminated"]
        for status in possible_statues:
            status_struct = state.get(status)
            if status_struct:
                return status_struct, status
        return None, None
    
    def write_network(self, pod_id: str) -> None:
        self.write_tuple(pod_id, ":host-ip", "$.status.hostIP")
        self.write_tuple(pod_id, ":pod-ip", "$.status.podIP")
    
    def write_node_id_reference(self, pod_id: str) -> None:
        node_name_match = parse("$.spec.nodeName").find(self.source)
        if len(node_name_match) == 0:
            return        
        for node_name in node_name_match:
            node_id = f":{node_name.value}"
            self.sink.add_tuple(pod_id, ":runs-on", node_id)
