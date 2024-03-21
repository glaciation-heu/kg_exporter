from typing import Any, Dict

from jsonpath_ng.ext import parse

from app.k8s_transform.transformer_base import TransformerBase
from app.kg.graph import Graph


class WorkloadToRDFTransformer(TransformerBase):
    def __init__(self, source: Dict[str, Any], sink: Graph):
        super().__init__(source, sink)

    def transform(self) -> None:
        name = self.get_id()
        self.sink.add_meta_property(name, "rdf:type", "gla:Workload")
        self.write_subclass_of(name, "rdf:subClassOf", "$.kind")

        self.write_collection(name, "gla:has-label", "$.metadata.labels")
        self.write_collection(name, "gla:has-annotation", "$.metadata.annotations")
        self.write_references(name)

    def write_subclass_of(self, name: str, property: str, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.add_meta_property(name, property, f"gla:{match.value}")
