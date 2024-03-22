from io import StringIO

from app.k8s_transform.test_base import TransformBaseTest
from app.k8s_transform.workload_transformer import WorkloadToRDFTransformer
from app.kg.inmemory_graph import InMemoryGraph
from app.serialize.turtle_serializer import TurtleSerialializer


class WorkloadTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_transform_turtle(self):
        self.transform_turtle("deployment")
        self.transform_turtle("statefulset")

    def transform_turtle(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        graph = InMemoryGraph()
        WorkloadToRDFTransformer(node_json, graph).transform()
        TurtleSerialializer().write(buffer, graph)
        self.assertEqual(buffer.getvalue(), node_turtle)
