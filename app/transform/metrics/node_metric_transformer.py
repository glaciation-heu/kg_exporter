from typing import List, Tuple

from app.core.repository.types import MetricQuery
from app.core.types import MetricValue
from app.kg.graph import Graph
from app.kg.iri import IRI
from app.transform.k8s.transformation_context import TransformationContext
from app.transform.metrics.metric_transformer import MetricToGraphTransformerBase
from app.transform.transformer_base import TransformerBase
from app.transform.upper_ontology_base import Aggregation, UpperOntologyBase


class NodeMetricToGraphTransformer(MetricToGraphTransformerBase, UpperOntologyBase):
    def __init__(self, metrics: List[Tuple[MetricQuery, MetricValue]], sink: Graph):
        MetricToGraphTransformerBase.__init__(self, metrics, sink)
        UpperOntologyBase.__init__(self, sink)

    def transform(self, context: TransformationContext) -> None:
        now = context.get_timestamp()
        for query, result in self.metrics:
            node_id = self.get_node_id(result.resource_id)
            timestamp = result.timestamp if not query.aggregation else now

            parent_resource_id = (
                node_id.dot(query.subresource) if query.subresource else node_id
            )
            description = (
                f"{query.subresource}.{query.measurement_id}"
                if query.subresource
                else query.measurement_id
            )
            measurement_id = parent_resource_id.dot(query.measurement_id).dot(
                f"{timestamp}"
            )
            property_id = IRI(self.GLACIATION_PREFIX, query.property)
            unit_id = IRI(self.GLACIATION_PREFIX, query.unit)
            source_id = IRI(self.GLACIATION_PREFIX, query.source)
            self.add_work_producing_resource(parent_resource_id, None)

            aggregation = (
                None
                if not query.aggregation
                else Aggregation(
                    function=query.aggregation.function,
                    starting_interval=now - (query.aggregation.period_seconds * 1000),
                    ending_interval=now,
                )
            )

            self.add_measurement(
                measurement_id,
                description,
                result.value,
                timestamp,
                aggregation,
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
