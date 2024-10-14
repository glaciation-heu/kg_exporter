import json
from io import StringIO

from app.core.repository.types import Aggregation, MetricQuery, ResultParserId
from app.core.types import MetricValue
from app.kg.inmemory_graph import InMemoryGraph
from app.kg.iri import IRI
from app.serialize.jsonld_serializer import JsonLDSerialializer
from app.serialize.turtle_serializer import TurtleSerialializer
from app.transform.metrics.pod_metric_transformer import PodMetricToGraphTransformer
from app.transform.metrics.test_base import MetricTransformTestBase
from app.transform.transformation_context import TransformationContext
from app.transform.transformer_base import TransformerBase


class PodMetricToGraphTransformerTest(MetricTransformTestBase):
    test_metrics = [
        (
            MetricQuery(
                measurement_id="CPU.Usage",
                subresource=None,
                source="cAdvisor",
                unit="coreseconds",
                aggregation=None,
                property="CPU.Usage",
                query="query",
                result_parser=ResultParserId.PROMETHEUS_PARSER,
            ),
            MetricValue(
                metric_id="my_metric",
                resource_id="pod1",
                timestamp=17100500,
                value=42.0,
            ),
        ),
        (
            MetricQuery(
                measurement_id="Energy.Usage",
                subresource=None,
                source="cAdvisor",
                unit="milliwatt",
                property="Energy.Usage",
                aggregation=Aggregation(function="average", period_seconds=300),
                query="query",
                result_parser=ResultParserId.PROMETHEUS_PARSER,
            ),
            MetricValue(
                metric_id="my_metric",
                resource_id="pod1",
                timestamp=17100500,
                value=42.0,
            ),
        ),
    ]

    def setUp(self):
        self.maxDiff = None

    def test_transform_turtle(self) -> None:
        node_turtle = self.load_turtle("pod1")

        buffer = StringIO()
        graph = InMemoryGraph()
        context = TransformationContext(123)
        PodMetricToGraphTransformer(
            self.test_metrics, {IRI(TransformerBase.CLUSTER_PREFIX, "pod1")}, graph
        ).transform(context)
        TurtleSerialializer().write(buffer, graph)
        self.assertEqual(buffer.getvalue(), node_turtle)

    def test_transform_jsonld(self) -> None:
        node_jsonld = self.load_jsonld("pod1")

        buffer = StringIO()
        graph = InMemoryGraph()
        context = TransformationContext(123)
        transformer = PodMetricToGraphTransformer(
            self.test_metrics, {IRI(TransformerBase.CLUSTER_PREFIX, "pod1")}, graph
        )
        transformer.transform(context)
        JsonLDSerialializer(self.get_jsonld_config()).write(buffer, graph)
        self.assertEqual(json.loads(buffer.getvalue()), node_jsonld)
