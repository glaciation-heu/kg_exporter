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

    def test_multiple_types(self):
        buffer = StringIO()
        graph = InMemoryGraph()
        obj_id = IRI("pref", "id1")
        graph.add_meta_property(obj_id, Graph.RDF_TYPE_IRI, IRI("pref", "MyNode"))
        graph.add_property(
            obj_id, IRI("pref", "str_type"), Literal("str_value", Literal.TYPE_STRING)
        )
        graph.add_property(
            obj_id, IRI("pref", "int_type"), Literal(42, Literal.TYPE_INT)
        )
        graph.add_property(
            obj_id, IRI("pref", "float_type"), Literal(42.00, Literal.TYPE_FLOAT)
        )
        graph.add_property(
            obj_id, IRI("pref", "bool_type"), Literal(True, Literal.TYPE_BOOL)
        )
        graph.add_property(
            obj_id,
            IRI("pref", "date_type"),
            Literal("2024-02-13T13:53:43Z", Literal.TYPE_DATE, "%Y-%m-%dT%H:%M:%S%z"),
        )

        TurtleSerialializer().write(buffer, graph)
        self.assertEqual(
            buffer.getvalue(),
            """pref:id1 rdf:type pref:MyNode .
pref:id1 pref:bool_type True^^<http://www.w3.org/2001/XMLSchema#boolean> .
pref:id1 pref:date_type "2024-02-13T13:53:43Z"^^<http://www.w3.org/2001/XMLSchema#dateTime> .
pref:id1 pref:float_type 42.0^^<http://www.w3.org/2001/XMLSchema#integer> .
pref:id1 pref:int_type 42^^<http://www.w3.org/2001/XMLSchema#integer> .
pref:id1 pref:str_type "str_value" .
""",
        )

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
