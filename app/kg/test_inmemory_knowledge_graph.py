from unittest import TestCase

from app.kg.inmemory_knowledge_graph import InMemoryKnowledgeGraph


class InMemoryKnowledgeGraphTest(TestCase):
    def test_empty(self):
        graph = InMemoryKnowledgeGraph()
        self.assertEqual(graph.get_ids(), set())

    def test_node(self):
        graph = InMemoryKnowledgeGraph()
        graph.add_property("id1", "rel1", "val11")
        self.assertEqual(
            graph.get_node_properties("id1"),
            {"rel1": "val11"},
        )
        graph.add_property_collection("id1", "rel2", {"val21", "val22"})
        graph.add_property("id1", "rel2", "val23")
        graph.add_meta_property("id1", "rel3", "meta")
        self.assertEqual(graph.get_ids(), {"id1"})
        self.assertEqual(
            graph.get_node_properties("id1"),
            {"rel1": "val11", "rel2": {"val21", "val22", "val23"}},
        )
        self.assertEqual(graph.get_node_meta_properties("id1"), {"rel3": "meta"})

    def test_edge(self):
        graph = InMemoryKnowledgeGraph()
        graph.add_relation("id1", "rel1", "id2")
        self.assertEqual(graph.get_node_relations("id1"), {"rel1": {"id2"}})
        graph.add_relation("id1", "rel1", "id3")
        self.assertEqual(graph.get_node_relations("id1"), {"rel1": {"id3", "id2"}})
        graph.add_relation_collection("id1", "rel1", {"id3", "id4"})
        graph.add_relation_collection("id2", "rel2", {"id3", "id4"})
        self.assertEqual(graph.get_ids(), {"id1", "id2", "id3", "id4"})
        self.assertEqual(graph.get_node_properties("id1"), {})
        self.assertEqual(graph.get_node_properties("id2"), {})
        self.assertEqual(graph.get_node_properties("id3"), {})
        self.assertEqual(graph.get_node_properties("id4"), {})
        self.assertEqual(
            graph.get_node_relations("id1"), {"rel1": {"id3", "id2", "id4"}}
        )
        self.assertEqual(graph.get_node_relations("id2"), {"rel2": {"id3", "id4"}})
