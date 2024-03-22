from io import StringIO

from app.k8s_transform.pod_transformer import PodToRDFTransformer
from app.k8s_transform.test_base import TransformBaseTest
from app.kg.inmemory_graph import InMemoryGraph
from app.serialize.turtle_serializer import TurtleSerialializer


class PodTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_transform_turtle(self):
        self.transform_turtle("pod1")
        self.transform_turtle("pod2")
        self.transform_turtle("pod3")

    def transform_turtle(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        graph = InMemoryGraph()
        PodToRDFTransformer(node_json, graph).transform()
        TurtleSerialializer().write(buffer, graph)
        self.assertEqual(buffer.getvalue(), node_turtle)
