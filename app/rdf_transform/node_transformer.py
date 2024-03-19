from typing import Any, Dict

from jsonpath_ng.ext import parse

from app.rdf_transform.transformer_base import TransformerBase
from app.rdf_transform.tuple_writer import TupleWriter


class NodesToRDFTransformer(TransformerBase):
    def __init__(self, source: Dict[str, Any], sink: TupleWriter):
        super().__init__(source, sink)

    def transform(self) -> None:
        node_id = self.get_node_id()
        self.sink.add_tuple(node_id, "rdf:type", ":Node")
        self.write_collection(node_id, ":has-label", "$.metadata.labels")
        self.write_collection(node_id, ":has-annotation", "$.metadata.annotations")

        self.write_network(node_id)
        self.write_resources(node_id, "allocatable")
        self.write_resources(node_id, "capacity")
        self.write_conditions(node_id)
        self.sink.flush()

    def write_resources(self, name: str, src: str) -> None:
        cpu_id = f"{name}.{src}.CPU"
        self.sink.add_tuple(cpu_id, "rdf:type", ":CPU")
        self.write_tuple(cpu_id, ":count", f"$.status.{src}.cpu")

        memory_id = f"{name}.{src}.Memory"
        self.sink.add_tuple(memory_id, "rdf:type", ":Memory")
        self.write_tuple(memory_id, ":bytes", f"$.status.{src}.memory")

        storage_id = f"{name}.{src}.Storage"
        self.sink.add_tuple(storage_id, "rdf:type", ":Storage")
        self.write_tuple(storage_id, ":bytes", f"$.status.{src}.ephemeral-storage")

        collection_resources = " ".join([cpu_id, memory_id, storage_id])
        self.sink.add_tuple(name, f":has-{src}-resource", f"({collection_resources})")

    def write_network(self, node_name: str) -> None:
        network_id = f"{node_name}.Network"
        self.sink.add_tuple(network_id, "rdf:type", ":Network")
        self.write_tuple(
            network_id,
            ":internal_ip",
            '$.status.addresses[?type == "InternalIP"].address',
        )
        self.write_tuple(
            network_id, ":hostname", '$.status.addresses[?type == "Hostname"].address'
        )
        self.sink.add_tuple(node_name, ":has-network", network_id)

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
            self.sink.add_tuple(condition_id, "rdf:type", ":NodeCondition")
            self.sink.add_tuple(condition_id, ":status", self.escape(status))
            self.sink.add_tuple(condition_id, ":reason", self.escape(reason))
        condition_ids_subject = " ".join(condition_ids)
        self.sink.add_tuple(node_name, ":has-condition", f"({condition_ids_subject})")

    def get_node_id(self) -> str:
        name = parse("$.metadata.name").find(self.source)[0].value
        resource_id = f":{name}"
        return resource_id
