from typing import Any, Dict

from app.k8s_transform.transformer_base import TransformerBase
from app.kg.knowledge_graph import KnowledgeGraph


class WorkloadToRDFTransformer(TransformerBase):
    def __init__(self, source: Dict[str, Any], sink: KnowledgeGraph):
        super().__init__(source, sink)

    def transform(self) -> None:
        name = self.get_id()
        self.sink.add_meta_property(name, "rdf:type", ":Workload")
        self.write_meta_tuple(name, "rdf:subClassOf", "$.kind")

        self.write_collection(name, ":has-label", "$.metadata.labels")
        self.write_collection(name, ":has-annotation", "$.metadata.annotations")
        self.write_references(name)
