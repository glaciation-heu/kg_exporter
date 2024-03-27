from typing import Any, Dict, Set, Tuple

import re

from jsonpath_ng.ext import parse

from app.kg.graph import Graph
from app.kg.iri import IRI
from app.kg.literal import Literal


class TransformerBase:
    CLUSTER_PREFIX = "cluster"
    GLACIATION_PREFIX = "gla"

    source: Dict[str, Any]
    sink: Graph

    def __init__(self, source: Dict[str, Any], sink: Graph):
        self.source = source
        self.sink = sink

    def write_references(self, node_id: IRI) -> None:
        references_match = parse("$.metadata.ownerReferences").find(self.source)
        if len(references_match) == 0:
            return
        for reference_match in references_match[0].value:
            reference, ref_type = self.get_reference_id(reference_match)
            self.sink.add_relation(
                reference, IRI(self.GLACIATION_PREFIX, "refers-to"), node_id
            )
            self.sink.add_meta_property(reference, Graph.RDF_TYPE_IRI, ref_type)

    def get_reference_id(self, reference: Dict[str, Any]) -> Tuple[IRI, IRI]:
        name = reference.get("name")
        uid = reference.get("uid")
        resource_type = IRI(self.GLACIATION_PREFIX, reference["kind"])
        resource_id = IRI(self.CLUSTER_PREFIX, f"{name}.{uid}")
        return resource_id, resource_type

    def write_tuple(self, name: IRI, property: IRI, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.add_property(
                name,
                property,
                Literal(self.escape(f"{match.value}"), Literal.TYPE_STRING),
            )

    def write_meta_tuple(self, name: IRI, property: IRI, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.add_meta_property(
                name,
                property,
                Literal(self.escape(f"{match.value}"), Literal.TYPE_STRING),
            )

    def write_tuple_from(
        self, source: Dict[str, Any], name: IRI, property: IRI, query: str
    ) -> None:
        for match in parse(query).find(source):
            self.sink.add_property(
                name,
                property,
                Literal(self.escape(f"{match.value}"), Literal.TYPE_STRING),
            )

    def write_tuple_list(self, name: IRI, property: IRI, query: str) -> None:
        for label, value in parse(query).find(self.source)[0].value.items():
            self.sink.add_property(
                name,
                property,
                Literal(self.escape(f"{label}:{value}"), Literal.TYPE_STRING),
            )

    def write_collection(self, name: IRI, property: IRI, query: str) -> None:
        subjects: Set[Literal] = set()
        found = parse(query).find(self.source)
        if len(found) == 0:
            return
        for label, value in found[0].value.items():
            subjects.add(
                Literal(
                    self.escape(f"{self.normalize(label)}:{self.normalize(value)}"),
                    Literal.TYPE_STRING,
                )
            )
        self.sink.add_property_collection(name, property, subjects)

    def escape(self, token: str) -> str:
        token = token.replace('"', '\\"')
        token = f"{token}"
        return token

    def normalize(self, value: str) -> str:
        return re.sub('["\n]', "", value)

    def get_id(self) -> IRI:
        name = parse("$.metadata.name").find(self.source)[0].value
        uid = parse("$.metadata.uid").find(self.source)[0].value
        resource_id = IRI(self.CLUSTER_PREFIX, f"{name}.{uid}")
        return resource_id

    def get_pod_id(self) -> IRI:
        name = parse("$.metadata.name").find(self.source)[0].value
        return IRI(self.CLUSTER_PREFIX, name)

    def get_node_id(self, node_resource: Dict[str, Any]) -> IRI:
        name = parse("$.metadata.name").find(node_resource)[0].value
        resource_id = IRI(self.CLUSTER_PREFIX, name)
        return resource_id
