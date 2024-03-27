from typing import Any, Dict

from app.k8s_transform.transformer_base import TransformerBase
from app.kg.graph import Graph
from app.kg.iri import IRI


class ReplicaSetToRDFTransformer(TransformerBase):
    def __init__(self, source: Dict[str, Any], sink: Graph):
        super().__init__(source, sink)

    def transform(self) -> None:
        replicaset_id = self.get_id()
        self.sink.add_meta_property(
            replicaset_id, Graph.RDF_TYPE_IRI, IRI(self.GLACIATION_PREFIX, "ReplicaSet")
        )
        self.write_collection(
            replicaset_id, IRI(self.GLACIATION_PREFIX, "has-label"), "$.metadata.labels"
        )
        self.write_collection(
            replicaset_id,
            IRI(self.GLACIATION_PREFIX, "has-annotation"),
            "$.metadata.annotations",
        )
        self.write_references(replicaset_id)
