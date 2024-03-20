from io import StringIO

from app.kg.inmemory_knowledge_graph import InMemoryKnowledgeGraph
from app.kg.turtle_serializer import TurtleSerialializer
from app.rdf_transform.node_transformer import NodesToRDFTransformer
from app.rdf_transform.test_base import TransformBaseTest


class NodeTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_transform(self):
        self.transform("master_node")
        self.transform("worker_node")

    def transform(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        graph = InMemoryKnowledgeGraph()
        NodesToRDFTransformer(node_json, graph).transform()
        TurtleSerialializer().write(buffer, graph)
        self.assertEqual(buffer.getvalue(), node_turtle)
