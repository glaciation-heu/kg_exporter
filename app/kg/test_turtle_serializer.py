from io import StringIO
from unittest import TestCase

from app.kg.graph import Graph
from app.kg.inmemory_graph import InMemoryGraph
from app.kg.turtle_serializer import TurtleSerialializer


class TurtleSerializerTest(TestCase):
    def setUp(self):
        pass

    def test_empty(self):
        buffer = StringIO()
        TurtleSerialializer().write(buffer, InMemoryGraph())
        self.assertEqual(buffer.getvalue(), "")

    def test_tuples(self):
        buffer = StringIO()
        TurtleSerialializer().write(buffer, self.sample_graph())
        expected = (
            """id1 rel3 meta .\nid1 rel1 val11 .\nid1 rel2 (val21 val22 val23) .\n"""
        )
        self.assertEqual(buffer.getvalue(), expected)

    def sample_graph(self) -> Graph:
        graph = InMemoryGraph()
        graph.add_property("id1", "rel1", "val11")
        graph.add_property_collection("id1", "rel2", {"val21", "val22"})
        graph.add_property("id1", "rel2", "val23")
        graph.add_meta_property("id1", "rel3", "meta")
        return graph
