
import json
from typing import Any, List, Tuple
from jsonpath_ng.ext import parse
from rdf_transform.tuple_writer import TupleWriter

class NodesToRDFTransformer:
    source: Any
    sink: TupleWriter

    def __init__(self, source: Any, sink: TupleWriter):
        self.source = source
        self.sink = sink

    def transform(self) -> None:
        name = self.get_id()
        self.sink.write(name, "rdf:type", ":Node")
        self.write_collection(name, ":has-label", '$.metadata.labels')
        self.write_collection(name, ":has-annotation", '$.metadata.annotations')
    
        self.write_network(name)
        self.write_resources(name, "allocatable")
        self.write_resources(name, "capacity")
        self.write_conditions(name)
        self.sink.flush()

    def write_resources(self, name: str, src: str) -> None:
        cpu_id = f"{name}.{src}.CPU"            
        self.sink.write(cpu_id, "rdf:type", ':CPU')
        self.write_tuple(cpu_id, ":count", f'$.status.{src}.cpu')

        memory_id = f"{name}.{src}.Memory"
        self.sink.write(memory_id, "rdf:type", ':Memory')
        self.write_tuple(memory_id, ":bytes", f'$.status.{src}.memory')

        storage_id = f"{name}.{src}.Storage"
        self.sink.write(storage_id, "rdf:type", ':Storage')
        self.write_tuple(storage_id, ":bytes", f'$.status.{src}.ephemeral-storage')

        collection_resources = " ".join([cpu_id, memory_id, storage_id])
        self.sink.write(name, f":has-{src}-resource", f"({collection_resources})")


    def write_network(self, node_name: str) -> None:
        network_id = f"{node_name}.Network"
        self.sink.write(network_id, "rdf:type", ":Network")
        self.write_tuple(network_id, ":internal_ip", '$.status.addresses[?type == "InternalIP"].address')    
        self.write_tuple(network_id, ":hostname", '$.status.addresses[?type == "Hostname"].address')    
        self.sink.write(node_name, ":has-network", network_id)

    def write_conditions(self, node_name: str) -> None:
        condition_ids = []
        for condition in parse("$.status.conditions").find(self.source)[0].value:
            condition_type = condition.get("type")
            if not condition_type:
                continue
            condition_id = f"{node_name}.NodeCondition.{condition_type}"            
            condition_ids.append(condition_id)
            status = condition.get("status")
            reason = condition.get("reason")
            self.sink.write(condition_id, "rdf:type", ":NodeCondition")
            self.sink.write(condition_id, ":status", self.escape(status))
            self.sink.write(condition_id, ":reason", self.escape(reason))
        condition_ids_subject = " ".join(condition_ids)
        self.sink.write(node_name, ":has-condition", f"({condition_ids_subject})")

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

    def get_id(self) -> str:
        name = parse('$.metadata.name').find(self.source)[0].value
        uid = parse('$.metadata.uid').find(self.source)[0].value
        resource_id = f":{name}.{uid}"
        return resource_id
