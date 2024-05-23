from typing import Any, Dict

from app.k8s_transform.transformation_context import TransformationContext
from app.k8s_transform.transformer_base import TransformerBase
from app.k8s_transform.upper_ontology_base import UpperOntologyBase
from app.kg.graph import Graph
from app.kg.iri import IRI


class ReplicaSetToRDFTransformer(TransformerBase, UpperOntologyBase):
    def __init__(self, source: Dict[str, Any], sink: Graph):
        TransformerBase.__init__(self, source, sink)
        UpperOntologyBase.__init__(self, sink)

    def transform(self, _: TransformationContext) -> None:
        replicaset_id = self.get_id()
        self.sink.add_meta_property(
            replicaset_id, Graph.RDF_TYPE_IRI, IRI(self.K8S_PREFIX, "ReplicaSet")
        )
        self.write_collection(
            replicaset_id, IRI(self.K8S_PREFIX, "has-label"), "$.metadata.labels"
        )
        self.write_collection(
            replicaset_id,
            IRI(self.K8S_PREFIX, "has-annotation"),
            "$.metadata.annotations",
        )
        self.write_references(replicaset_id)
