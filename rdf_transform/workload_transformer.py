
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

        self.write_collection(name, ":label", '$.metadata.labels')
        self.write_collection(name, ":annotation", '$.metadata.annotations')
    
        self.sink.flush()

    def write_tuple(self, name: str, property: str, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.write(name, property, self.escape(f"{match.value}"))

    def write_collection(self, name: str, property: str, query: str) -> None:
        subjects = []
        for label, value in parse(query).find(self.source)[0].value.items():
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
