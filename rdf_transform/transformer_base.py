import json
import re
from typing import Any, Dict, List, Optional, Tuple
from jsonpath_ng.ext import parse
from rdf_transform.tuple_writer import TupleWriter

class TransformerBase:
    source: Dict[str, Any]

    def __init__(self, source: Dict[str, Any]):
        self.source = source

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
            self.sink.add_tuple(reference, ":refers-to", node_id)

    def get_reference_id(self, reference: Dict[str, Any]) -> str:        
        name = reference.get('name')
        uid = reference.get('uid')
        resource_id = f":{name}.{uid}"
        return resource_id
    
    def write_tuple(self, name: str, property: str, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.add_tuple(name, property, self.escape(f"{match.value}"))

    def write_tuple_from(self, source: Dict[str, Any], name: str, property: str, query: str) -> None:
        for match in parse(query).find(source):
            self.sink.add_tuple(name, property, self.escape(f"{match.value}"))

    def write_tuple_list(self, name: str, property: str, query: str) -> None:
        for label, value in parse(query).find(self.source)[0].value.items():
            self.sink.add_tuple(name, property, self.escape(f"{label}:{value}"))

    def write_collection(self, name: str, property: str, query: str) -> None:
        subjects = []
        found = parse(query).find(self.source)
        if len(found) == 0:
            return
        for label, value in found[0].value.items():
            subjects.append(self.escape(f"{self.normalize(label)}:{self.normalize(value)}"))
        collection_subject = " ".join(subjects)
        self.sink.add_tuple(name, property, f"({collection_subject})")

    def escape(self, token: str) -> str:
        token = token.replace("\"", "\\\"")
        token = f"\"{token}\""
        return token
    
    def normalize(self, value: str) -> str:
        return re.sub("[\"\n]", "", value)

    def get_id(self) -> str:
        name = parse('$.metadata.name').find(self.source)[0].value
        uid = parse('$.metadata.uid').find(self.source)[0].value
        resource_id = f":{name}.{uid}"
        return resource_id

    def get_pod_id(self) -> str:
        name = parse('$.metadata.name').find(self.source)[0].value
        return f":{name}"

