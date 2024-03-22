from io import StringIO

from app.k8s_transform.node_transformer import NodesToRDFTransformer
from app.k8s_transform.test_base import TransformBaseTest
from app.kg.inmemory_graph import InMemoryGraph
from app.serialize.turtle_serializer import TurtleSerialializer


class NodeTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_transform_turtle(self):
        self.transform_turtle("master_node")
        self.transform_turtle("worker_node")

    def transform_turtle(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        graph = InMemoryGraph()
        NodesToRDFTransformer(node_json, graph).transform()
        TurtleSerialializer().write(buffer, graph)
        self.assertEqual(buffer.getvalue(), node_turtle)
