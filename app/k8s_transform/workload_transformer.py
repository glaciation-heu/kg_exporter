from typing import Any, Dict

from jsonpath_ng.ext import parse

from app.k8s_transform.transformation_context import TransformationContext
from app.k8s_transform.transformer_base import TransformerBase
from app.k8s_transform.upper_ontology_base import UpperOntologyBase
from app.kg.graph import Graph
from app.kg.iri import IRI


class WorkloadToRDFTransformer(TransformerBase, UpperOntologyBase):
    def __init__(self, source: Dict[str, Any], sink: Graph):
        TransformerBase.__init__(self, source, sink)
        UpperOntologyBase.__init__(self, sink)

    def transform(self, _: TransformationContext) -> None:
        name = self.get_id()
        self.sink.add_meta_property(
            name, Graph.RDF_TYPE_IRI, IRI(self.K8S_PREFIX, "Workload")
        )
        self.write_subclass_of(name, Graph.RDF_SUBCLASSOF_IRI, "$.kind")

        self.write_collection(
            name, IRI(self.K8S_PREFIX, "has-label"), "$.metadata.labels"
        )
        self.write_collection(
            name,
            IRI(self.K8S_PREFIX, "has-annotation"),
            "$.metadata.annotations",
        )
        self.write_references(name)

    def write_subclass_of(self, name: IRI, property: IRI, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.add_meta_property(
                name, property, IRI(self.K8S_PREFIX, match.value)
            )
