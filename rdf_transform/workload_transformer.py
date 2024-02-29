
import json
from typing import Any, List, Tuple
from jsonpath_ng.ext import parse
from rdf_transform.tuple_writer import TupleWriter

class WorkloadToRDFTransformer:
    source: Any
    sink: TupleWriter

    def __init__(self, source: Any, sink: TupleWriter):
        self.source = source
        self.sink = sink

    def transform(self) -> None:
        name = self.get_id()
        self.sink.write(name, "rdf:type", ":Workload")
        self.write_tuple(name, "rdf:subClassOf", f'$.kind')

        self.write_collection(name, ":has-label", '$.metadata.labels')
        self.write_collection(name, ":has-annotation", '$.metadata.annotations')
        self.write_references(name)

        self.sink.flush()

    def write_tuple(self, name: str, property: str, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.write(name, property, self.escape(f"{match.value}"))

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
