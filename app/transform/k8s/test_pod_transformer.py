import json
from io import StringIO

from app.kg.inmemory_graph import InMemoryGraph
from app.serialize.jsonld_serializer import JsonLDSerialializer
from app.serialize.turtle_serializer import TurtleSerialializer
from app.transform.k8s.pod_transformer import PodToRDFTransformer
from app.transform.k8s.test_base import TransformBaseTest
from app.transform.transformation_context import TransformationContext


class PodTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_transform_turtle(self):
        self.transform_turtle("pod1")
        self.transform_turtle("pod2")
        self.transform_turtle("pod3")
        self.transform_turtle("workload_pod")

    def transform_turtle(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        graph = InMemoryGraph()
        context = TransformationContext(123)
        PodToRDFTransformer(node_json, graph).transform(context)
        TurtleSerialializer().write(buffer, graph)
        self.assertEqual(buffer.getvalue(), node_turtle)

    def test_transform_jsonld(self):
        self.transform_jsonld("pod1")
        self.transform_jsonld("pod2")
        self.transform_jsonld("pod3")
        self.transform_jsonld("workload_pod")

    def transform_jsonld(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_jsonld = self.load_jsonld(file_id)

        buffer = StringIO()
        graph = InMemoryGraph()
        context = TransformationContext(123)
        transformer = PodToRDFTransformer(node_json, graph)
        transformer.transform(context)
        JsonLDSerialializer(self.get_jsonld_config()).write(buffer, graph)
        self.assertEqual(json.loads(buffer.getvalue()), node_jsonld)
