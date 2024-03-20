from io import StringIO

from app.rdf_transform.inmemory_knowledge_graph import InMemoryKnowledgeGraph
from app.rdf_transform.replicaset_transformer import ReplicaSetToRDFTransformer
from app.rdf_transform.test_base import TransformBaseTest
from app.rdf_transform.turtle_serializer import TurtleSerialializer


class ReplicaSetTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_transform(self):
        self.transform("replicaset")

    def transform(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        graph = InMemoryKnowledgeGraph()
        ReplicaSetToRDFTransformer(node_json, graph).transform()
        TurtleSerialializer().write(buffer, graph)
        self.assertEqual(buffer.getvalue(), node_turtle)
