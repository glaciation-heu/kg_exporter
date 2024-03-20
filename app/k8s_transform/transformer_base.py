from typing import Any, Dict, Set

import re

from jsonpath_ng.ext import parse

from app.kg.graph import Graph


class TransformerBase:
    source: Dict[str, Any]
    sink: Graph

    def __init__(self, source: Dict[str, Any], sink: Graph):
        self.source = source
        self.sink = sink

    def write_references(self, node_id: str) -> None:
        references_match = parse("$.metadata.ownerReferences").find(self.source)
        if len(references_match) == 0:
            return
        for reference_match in references_match[0].value:
            reference = self.get_reference_id(reference_match)
            self.sink.add_relation(reference, ":refers-to", node_id)

    def get_reference_id(self, reference: Dict[str, Any]) -> str:
        name = reference.get("name")
        uid = reference.get("uid")
        resource_id = f":{name}.{uid}"
        return resource_id

    def write_tuple(self, name: str, property: str, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.add_property(name, property, self.escape(f"{match.value}"))

    def write_meta_tuple(self, name: str, property: str, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.add_meta_property(name, property, self.escape(f"{match.value}"))

    def write_tuple_from(
        self, source: Dict[str, Any], name: str, property: str, query: str
    ) -> None:
        for match in parse(query).find(source):
            self.sink.add_property(name, property, self.escape(f"{match.value}"))

    def write_tuple_list(self, name: str, property: str, query: str) -> None:
        for label, value in parse(query).find(self.source)[0].value.items():
            self.sink.add_property(name, property, self.escape(f"{label}:{value}"))

    def write_collection(self, name: str, property: str, query: str) -> None:
        subjects: Set[str | int | bool | float] = set()
        found = parse(query).find(self.source)
        if len(found) == 0:
            return
        for label, value in found[0].value.items():
            subjects.add(
                self.escape(f"{self.normalize(label)}:{self.normalize(value)}")
            )
        self.sink.add_property_collection(name, property, subjects)

    def escape(self, token: str) -> str:
        token = token.replace('"', '\\"')
        token = f'"{token}"'
        return token

    def normalize(self, value: str) -> str:
        return re.sub('["\n]', "", value)

    def get_id(self) -> str:
        name = parse("$.metadata.name").find(self.source)[0].value
        uid = parse("$.metadata.uid").find(self.source)[0].value
        resource_id = f":{name}.{uid}"
        return resource_id

    def get_pod_id(self) -> str:
        name = parse("$.metadata.name").find(self.source)[0].value
        return f":{name}"
