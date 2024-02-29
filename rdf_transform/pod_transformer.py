
import json
from typing import Any, List, Tuple
from jsonpath_ng.ext import parse
from rdf_transform.tuple_writer import TupleWriter

class PodToRDFTransformer:
    source: Any
    sink: TupleWriter

    def __init__(self, source: Any, sink: TupleWriter):
        self.source = source
        self.sink = sink

    def transform(self) -> None:
        pod_id = self.get_pod_id()
        self.sink.write(pod_id, "rdf:type", ":Pod")
        self.write_collection(pod_id, ":has-label", '$.metadata.labels')
        self.write_collection(pod_id, ":has-annotation", '$.metadata.annotations')
        self.write_references(pod_id)
        self.write_node_id_reference(pod_id) 
        self.write_containers(pod_id)

        self.write_network(pod_id)

        self.sink.flush()

    def write_containers(self, pod_id: str) -> None:
        container_ids = []
        
        container_status_matches = parse("$.status.containerStatuses").find(self.source)
        if len(container_status_matches) == 0:
            return
        for container_match in container_status_matches[0].value:
            container_id = container_match.get("containerID")
            if not container_id:
                continue
            name = container_match.get("name")
            restart_count = container_match.get("restartCount")        
            container_ids.append(container_id)
            self.sink.write(container_id, "rdf:type", ":Container")
            self.sink.write(container_id, ":has-name", self.escape(name))
            self.sink.write(container_id, ":restart-count", str(restart_count))

            container_spec_matches = parse("$.spec.containers").find(self.source)

        container_ids = " ".join(container_ids)
        self.sink.write(pod_id, ":has-container", f"({container_ids})")


            # {
            #     "containerID": "containerd://0ce09d1e8fdff70a58902bb3e73efafa76035dddbe9cec8b4115ac80d09f9963",
            #     "image": "registry.k8s.io/coredns/coredns:v1.9.3",
            #     "imageID": "registry.k8s.io/coredns/coredns@sha256:8e352a029d304ca7431c6507b56800636c321cb52289686a581ab70aaa8a2e2a",
            #     "lastState": {},
            #     "name": "coredns",
            #     "ready": true,
            #     "restartCount": 0,
            #     "started": true,
            #     "state": {
            #         "running": {
            #             "startedAt": "2024-02-13T13:53:44Z"
            #         }
            #     }
            # }

    def write_network(self, pod_id: str) -> None:
        self.write_tuple(pod_id, ":in-phase", "$.status.phase")
        self.write_tuple(pod_id, ":host-ip", "$.status.hostIP")
        self.write_tuple(pod_id, ":pod-ip", "$.status.podIP")
        self.write_tuple(pod_id, ":qos-class", "$.status.qosClass")
        self.write_tuple(pod_id, ":start-time", "$.status.startTime")        

    def write_if_present(self, pod_id: str, property: str, path: str) -> None:
        phase_match = parse(path).find(self.source)
        if len(phase_match) == 0:
            return
        self.write_tuple(pod_id, property, )


    def write_references(self, node_id: str) -> None:
        references_match = parse("$.metadata.ownerReferences").find(self.source)
        if len(references_match) == 0:
            return
        for reference_match in references_match[0].value:
            reference = self.get_reference_id(reference_match)
            self.sink.write(reference, ":refers-to", node_id)

    def get_reference_id(self, reference: Any) -> str:        
        name = reference.get('name')
        uid = reference.get('uid')
        resource_id = f":{name}.{uid}"
        return resource_id
    
    def write_node_id_reference(self, pod_id: str) -> None:
        node_name_match = parse("$.spec.nodeName").find(self.source)
        if len(node_name_match) == 0:
            return        
        for node_name in node_name_match:
            node_id = f":{node_name.value}"
            self.sink.write(pod_id, ":runs-on", node_id)


    def write_tuple(self, name: str, property: str, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.write(name, property, self.escape(f"{match.value}"))

    def write_tuple_list(self, name: str, property: str, query: str) -> None:
        for label, value in parse(query).find(self.source)[0].value.items():
            self.sink.write(name, property, self.escape(f"{label}:{value}"))

    def write_collection(self, name: str, property: str, query: str) -> None:
        subjects = []
        found = parse(query).find(self.source)
        if len(found) == 0:
            return
        for label, value in found[0].value.items():
            subjects.append(self.escape(f"{label}:{value}"))
        collection_subject = " ".join(subjects)
        self.sink.write(name, property, f"({collection_subject})")

    def escape(self, token: str) -> str:
        token = token.replace("\"", "\\\"")
        token = f"\"{token}\""
        return token

    def get_pod_id(self) -> str:
        name = parse('$.metadata.name').find(self.source)[0].value
        return f":{name}"
