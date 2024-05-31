from unittest import TestCase

from app.kg.inmemory_graph import InMemoryGraph
from app.kg.iri import IRI
from app.kg.literal import Literal


class InMemoryGraphTest(TestCase):
    def test_empty(self):
        graph = InMemoryGraph()
        self.assertEqual(graph.get_ids(), set())

    def test_node(self):
        graph = InMemoryGraph()
        graph.add_property(IRI("", "id1"), IRI("", "rel1"), Literal("val11", "str"))
        self.assertEqual(
            graph.get_node_properties(IRI("", "id1")),
            {IRI("", "rel1"): Literal("val11", "str")},
        )
        graph.add_property_collection(
            IRI("", "id1"),
            IRI("", "rel2"),
            {Literal("val21", "str"), Literal("val22", "str")},
        )
        graph.add_property(IRI("", "id1"), IRI("", "rel2"), Literal("val23", "str"))
        graph.add_meta_property(IRI("", "id1"), IRI("", "rel3"), Literal("meta", "str"))
        self.assertEqual(graph.get_ids(), {IRI("", "id1")})
        self.assertEqual(
            graph.get_node_properties(IRI("", "id1")),
            {
                IRI("", "rel1"): Literal("val11", "str"),
                IRI("", "rel2"): {
                    Literal("val21", "str"),
                    Literal("val22", "str"),
                    Literal("val23", "str"),
                },
            },
        )
        self.assertEqual(
            graph.get_node_meta_properties(IRI("", "id1")),
            {IRI("", "rel3"): Literal("meta", "str")},
        )

    def test_edge(self):
        graph = InMemoryGraph()
        graph.add_relation(IRI("", "id1"), IRI("", "rel1"), IRI("", "id2"))
        self.assertEqual(
            graph.get_node_relations(IRI("", "id1")),
            {IRI("", "rel1"): {IRI("", "id2")}},
        )
        graph.add_relation(IRI("", "id1"), IRI("", "rel1"), IRI("", "id3"))
        self.assertEqual(
            graph.get_node_relations(IRI("", "id1")),
            {IRI("", "rel1"): {IRI("", "id3"), IRI("", "id2")}},
        )
        graph.add_relation_collection(
            IRI("", "id1"), IRI("", "rel1"), {IRI("", "id3"), IRI("", "id4")}
        )
        graph.add_relation_collection(
            IRI("", "id2"), IRI("", "rel2"), {IRI("", "id3"), IRI("", "id4")}
        )
        self.assertEqual(
            graph.get_ids(),
            {IRI("", "id1"), IRI("", "id2"), IRI("", "id3"), IRI("", "id4")},
        )
        self.assertEqual(graph.get_node_properties(IRI("", "id1")), {})
        self.assertEqual(graph.get_node_properties(IRI("", "id2")), {})
        self.assertEqual(graph.get_node_properties(IRI("", "id3")), {})
        self.assertEqual(graph.get_node_properties(IRI("", "id4")), {})
        self.assertEqual(
            graph.get_node_relations(IRI("", "id1")),
            {IRI("", "rel1"): {IRI("", "id3"), IRI("", "id2"), IRI("", "id4")}},
        )
        self.assertEqual(
            graph.get_node_relations(IRI("", "id2")),
            {IRI("", "rel2"): {IRI("", "id3"), IRI("", "id4")}},
        )

    def test_equality(self):
        graph1 = InMemoryGraph()
        graph2 = InMemoryGraph()
        self.assertEqual(graph1, graph2)

        graph1.add_property(
            IRI("", "id1"), IRI("", "rel1"), Literal("1", Literal.TYPE_INT)
        )
        self.assertNotEqual(graph1, graph2)

        graph2.add_property(
            IRI("", "id1"), IRI("", "rel1"), Literal("1", Literal.TYPE_INT)
        )
        self.assertEqual(graph1, graph2)

        graph1.add_relation(IRI("", "id1"), IRI("", "rel2"), IRI("", "id2"))
        self.assertNotEqual(graph1, graph2)

        graph2.add_relation(IRI("", "id1"), IRI("", "rel2"), IRI("", "id2"))
        self.assertEqual(graph1, graph2)

        graph1.add_meta_property(
            IRI("", "id1"), IRI("", "rel3"), Literal("1", Literal.TYPE_INT)
        )
        self.assertNotEqual(graph1, graph2)

        graph2.add_meta_property(
            IRI("", "id1"), IRI("", "rel3"), Literal("1", Literal.TYPE_INT)
        )
        self.assertEqual(graph1, graph2)
