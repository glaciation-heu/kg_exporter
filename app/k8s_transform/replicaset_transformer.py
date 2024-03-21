from typing import Any, Dict

from app.k8s_transform.transformer_base import TransformerBase
from app.kg.graph import Graph


class ReplicaSetToRDFTransformer(TransformerBase):
    def __init__(self, source: Dict[str, Any], sink: Graph):
        super().__init__(source, sink)

    def transform(self) -> None:
        name = self.get_id()
        self.sink.add_meta_property(name, "rdf:type", "gla:ReplicaSet")
        self.write_collection(name, "gla:has-label", "$.metadata.labels")
        self.write_collection(name, "gla:has-annotation", "$.metadata.annotations")
        self.write_references(name)
