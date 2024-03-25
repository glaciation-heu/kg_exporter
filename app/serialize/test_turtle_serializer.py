from io import StringIO
from unittest import TestCase

from app.kg.graph import Graph
from app.kg.inmemory_graph import InMemoryGraph
from app.kg.iri import IRI
from app.kg.literal import Literal
from app.serialize.turtle_serializer import TurtleSerialializer


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
        expected = """pref:id1 pref:rel3 "meta" .\npref:id1 pref:rel1 "val11" .
pref:id1 pref:rel2 ("val21" "val22" "val23") .
"""
        self.assertEqual(buffer.getvalue(), expected)

    def sample_graph(self) -> Graph:
        graph = InMemoryGraph()
        graph.add_property(
            IRI("pref", "id1"), IRI("pref", "rel1"), Literal("val11", "str")
        )
        graph.add_property_collection(
            IRI("pref", "id1"),
            IRI("pref", "rel2"),
            {Literal("val21", "str"), Literal("val22", "str")},
        )
        graph.add_property(
            IRI("pref", "id1"), IRI("pref", "rel2"), Literal("val23", "str")
        )
        graph.add_meta_property(
            IRI("pref", "id1"), IRI("pref", "rel3"), Literal("meta", "str")
        )
        return graph
