from io import StringIO
from unittest import TestCase

from app.kg.inmemory_knowledge_graph import InMemoryKnowledgeGraph
from app.kg.knowledge_graph import KnowledgeGraph
from app.kg.turtle_serializer import TurtleSerialializer


class TurtleWriterTest(TestCase):
    def setUp(self):
        pass

    def test_empty(self):
        buffer = StringIO()
        TurtleSerialializer().write(buffer, InMemoryKnowledgeGraph())
        self.assertEqual(buffer.getvalue(), "")

    def test_tuples(self):
        buffer = StringIO()
        TurtleSerialializer().write(buffer, self.sample_graph())
        expected = (
            """id1 rel3 meta .\nid1 rel1 val11 .\nid1 rel2 (val21 val22 val23) .\n"""
        )
        self.assertEqual(buffer.getvalue(), expected)

    def sample_graph(self) -> KnowledgeGraph:
        graph = InMemoryKnowledgeGraph()
        graph.add_property("id1", "rel1", "val11")
        graph.add_property_collection("id1", "rel2", {"val21", "val22"})
        graph.add_property("id1", "rel2", "val23")
        graph.add_meta_property("id1", "rel3", "meta")
        return graph
