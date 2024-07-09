import json
from io import StringIO

from app.core.repository.types import MetricQuery, ResultParserId
from app.core.types import MetricValue
from app.kg.inmemory_graph import InMemoryGraph
from app.serialize.jsonld_serializer import JsonLDSerialializer
from app.serialize.turtle_serializer import TurtleSerialializer
from app.transform.k8s.transformation_context import TransformationContext
from app.transform.metrics.node_metric_transformer import NodeMetricToGraphTransformer
from app.transform.metrics.test_base import MetricTransformTestBase


class NodeMetricToGraphTransformerTest(MetricTransformTestBase):
    test_metrics = [
        (
            MetricQuery(
                measurement_id="Usage",
                subresource="CPU",
                source="cAdvisor",
                unit="coreseconds",
                property="CPU.Usage",
                query="query",
                result_parser=ResultParserId.PROMETHEUS_PARSER,
            ),
            MetricValue(
                metric_id="my_metric",
                resource_id="worker1",
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
                query="query",
                result_parser=ResultParserId.PROMETHEUS_PARSER,
            ),
            MetricValue(
                metric_id="my_metric",
                resource_id="worker1",
                timestamp=17100500,
                value=42.0,
            ),
        ),
    ]

    def setUp(self):
        self.maxDiff = None

    def test_transform_turtle(self) -> None:
        node_turtle = self.load_turtle("node")

        buffer = StringIO()
        graph = InMemoryGraph()
        context = TransformationContext(123)
        NodeMetricToGraphTransformer(self.test_metrics, graph).transform(context)
        TurtleSerialializer().write(buffer, graph)
        self.assertEqual(buffer.getvalue(), node_turtle)

    def test_transform_jsonld(self) -> None:
        node_jsonld = self.load_jsonld("node")

        buffer = StringIO()
        graph = InMemoryGraph()
        context = TransformationContext(123)
        transformer = NodeMetricToGraphTransformer(self.test_metrics, graph)
        transformer.transform(context)
        JsonLDSerialializer(self.get_jsonld_config()).write(buffer, graph)
        self.assertEqual(json.loads(buffer.getvalue()), node_jsonld)
