from io import StringIO

from app.k8s_transform.pod_transformer import PodToRDFTransformer
from app.k8s_transform.test_base import TransformBaseTest
from app.kg.inmemory_knowledge_graph import InMemoryKnowledgeGraph
from app.kg.turtle_serializer import TurtleSerialializer


class PodTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_transform(self):
        self.transform("pod1")
        self.transform("pod2")
        self.transform("pod3")

    def transform(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        graph = InMemoryKnowledgeGraph()
        PodToRDFTransformer(node_json, graph).transform()
        TurtleSerialializer().write(buffer, graph)
        self.assertEqual(buffer.getvalue(), node_turtle)
