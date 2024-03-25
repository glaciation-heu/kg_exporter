from typing import Any, Dict

from jsonpath_ng.ext import parse

from app.k8s_transform.transformer_base import TransformerBase
from app.kg.graph import Graph
from app.kg.iri import IRI
from app.kg.literal import Literal
from app.kg.types import RelationSet


class NodesToRDFTransformer(TransformerBase):
    def __init__(self, source: Dict[str, Any], sink: Graph):
        super().__init__(source, sink)

    def transform(self) -> None:
        node_id = self.get_node_id()
        self.sink.add_meta_property(
            node_id, Graph.RDF_TYPE_IRI, IRI(self.GLACIATION_PREFIX, "Node")
        )
        self.write_collection(
            node_id, IRI(self.GLACIATION_PREFIX, "has-label"), "$.metadata.labels"
        )
        self.write_collection(
            node_id,
            IRI(self.GLACIATION_PREFIX, "has-annotation"),
            "$.metadata.annotations",
        )

        self.write_network(node_id)
        self.write_resources(node_id, "allocatable")
        self.write_resources(node_id, "capacity")
        self.write_conditions(node_id)

    def write_resources(self, name: IRI, src: str) -> None:
        cpu_id = IRI(self.CLUSTER_PREFIX, f"{name.value}.{src}.CPU")
        self.sink.add_meta_property(
            cpu_id, Graph.RDF_TYPE_IRI, IRI(self.GLACIATION_PREFIX, "CPU")
        )
        self.write_tuple(
            cpu_id, IRI(self.GLACIATION_PREFIX, "count"), f"$.status.{src}.cpu"
        )

        memory_id = IRI(self.CLUSTER_PREFIX, f"{name.value}.{src}.Memory")
        self.sink.add_meta_property(
            memory_id, Graph.RDF_TYPE_IRI, IRI(self.GLACIATION_PREFIX, "Memory")
        )
        self.write_tuple(
            memory_id, IRI(self.GLACIATION_PREFIX, "bytes"), f"$.status.{src}.memory"
        )

        storage_id = IRI(self.CLUSTER_PREFIX, f"{name.value}.{src}.Storage")
        self.sink.add_meta_property(
            storage_id, Graph.RDF_TYPE_IRI, IRI(self.GLACIATION_PREFIX, "Storage")
        )
        self.write_tuple(
            storage_id,
            IRI(self.GLACIATION_PREFIX, "bytes"),
            f"$.status.{src}.ephemeral-storage",
        )

        resources = {cpu_id, memory_id, storage_id}
        self.sink.add_relation_collection(
            name, IRI(self.GLACIATION_PREFIX, f"has-{src}-resource"), resources
        )

    def write_network(self, node_name: IRI) -> None:
        network_id = IRI(self.CLUSTER_PREFIX, f"{node_name.value}.Network")
        self.sink.add_meta_property(
            network_id, Graph.RDF_TYPE_IRI, IRI(self.GLACIATION_PREFIX, "Network")
        )
        self.write_tuple(
            network_id,
            IRI(self.GLACIATION_PREFIX, "internal_ip"),
            '$.status.addresses[?type == "InternalIP"].address',
        )
        self.write_tuple(
            network_id,
            IRI(self.GLACIATION_PREFIX, "hostname"),
            '$.status.addresses[?type == "Hostname"].address',
        )
        self.sink.add_relation(
            node_name, IRI(self.GLACIATION_PREFIX, "has-network"), network_id
        )

    def write_conditions(self, node_name: IRI) -> None:
        condition_ids: RelationSet = set()
        for condition in parse("$.status.conditions").find(self.source)[0].value:
            condition_type = condition.get("type")
            if not condition_type:
                continue
            condition_id = IRI(
                self.CLUSTER_PREFIX, f"{node_name.value}.NodeCondition.{condition_type}"
            )
            condition_ids.add(condition_id)
            status = condition.get("status")
            reason = condition.get("reason")
            self.sink.add_meta_property(
                condition_id,
                Graph.RDF_TYPE_IRI,
                IRI(self.GLACIATION_PREFIX, "NodeCondition"),
            )
            self.sink.add_property(
                condition_id,
                IRI(self.GLACIATION_PREFIX, "status"),
                Literal(self.escape(status), "str"),
            )
            self.sink.add_property(
                condition_id,
                IRI(self.GLACIATION_PREFIX, "reason"),
                Literal(self.escape(reason), "str"),
            )
        self.sink.add_relation_collection(
            node_name, IRI(self.GLACIATION_PREFIX, "has-condition"), condition_ids
        )

    def get_node_id(self) -> IRI:
        name = parse("$.metadata.name").find(self.source)[0].value
        resource_id = IRI(self.CLUSTER_PREFIX, f"{name}")
        return resource_id
