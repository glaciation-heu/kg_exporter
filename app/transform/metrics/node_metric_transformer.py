from typing import List, Tuple

from app.core.repository.types import MetricQuery
from app.core.types import MetricValue
from app.kg.graph import Graph
from app.kg.iri import IRI
from app.transform.k8s.transformation_context import TransformationContext
from app.transform.k8s.transformer_base import TransformerBase
from app.transform.k8s.upper_ontology_base import UpperOntologyBase
from app.transform.metrics.metric_transformer import MetricToGraphTransformerBase


class NodeMetricToGraphTransformer(MetricToGraphTransformerBase, UpperOntologyBase):
    def __init__(self, metrics: List[Tuple[MetricQuery, MetricValue]], sink: Graph):
        MetricToGraphTransformerBase.__init__(self, metrics, sink)
        UpperOntologyBase.__init__(self, sink)

    def transform(self, context: TransformationContext) -> None:
        for query, result in self.metrics:
            node_id = self.get_node_id(result.resource_id)
            parent_resource_id = (
                node_id.dot(query.subresource) if query.subresource else node_id
            )
            measurement_id = parent_resource_id.dot(query.measurement_id)
            property_id = IRI(self.GLACIATION_PREFIX, query.property)
            unit_id = IRI(self.GLACIATION_PREFIX, query.unit)
            source_id = IRI(self.GLACIATION_PREFIX, query.source)
            self.add_work_producing_resource(parent_resource_id, None)
            self.add_measurement(
                measurement_id,
                query.measurement_id,
                result.value,
                result.timestamp,
                unit_id,
                property_id,
                source_id,
            )
            self.sink.add_relation(
                parent_resource_id, self.HAS_MEASUREMENT, measurement_id
            )

    def get_node_id(self, name: str) -> IRI:
        resource_id = IRI(TransformerBase.CLUSTER_PREFIX, name)
        return resource_id
