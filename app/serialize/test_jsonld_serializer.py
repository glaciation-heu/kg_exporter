import json
from io import StringIO
from unittest import TestCase

from app.kg.graph import Graph
from app.kg.inmemory_graph import InMemoryGraph
from app.serialize.jsonld_serializer import JsonLDSerialializer


class JsonLDSerializerTest(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_empty(self):
        buffer = StringIO()
        JsonLDSerialializer(dict()).write(buffer, InMemoryGraph())
        self.assertEqual(buffer.getvalue(), "[]")

    def test_no_context(self):
        buffer = StringIO()
        graph = InMemoryGraph()
        graph.add_meta_property("id1", "rdf:type", ":MyNode")
        JsonLDSerialializer(dict()).write(buffer, graph)
        expected = """[{"@id": "id1", "@type": ":MyNode", "rdf:type": ":MyNode"}]"""
        self.assertEqual(buffer.getvalue(), expected)

    def test_full(self):
        buffer = StringIO()
        contexts = {
            ":MyNode": {
                "MyNode": "http://example.com/MyNode",
                "rel1": "http://example.com/MyNode/rel1",
                "rel2": "http://example.com/MyNode/rel2",
                "connects": "http://example.com/MyNode/connects",
            },
            ":MyNode2": {
                "prop2": "http://example.com/MyNode2/prop2",
                "MyNode2": "http://example.com/MyNode2",
            },
        }
        JsonLDSerialializer(contexts).write(buffer, self.sample_graph())
        expected = [
            {
                "@id": "id1",
                "@type": ":MyNode",
                "@context": {
                    "MyNode": "http://example.com/MyNode",
                    "rel1": "http://example.com/MyNode/rel1",
                    "rel2": "http://example.com/MyNode/rel2",
                    "connects": "http://example.com/MyNode/connects",
                },
                "rdf:type": ":MyNode",
                "rel1": "val11",
                "rel2": {"@set": ["val21", "val22", "val23"]},
                "connects": "id2",
            },
            {
                "@id": "id2",
                "@type": ":MyNode2",
                "@context": {
                    "prop2": "http://example.com/MyNode2/prop2",
                    "MyNode2": "http://example.com/MyNode2",
                },
                "prop2": "val2",
                "rdf:type": ":MyNode2",
            },
        ]
        self.assertEqual(buffer.getvalue(), json.dumps(expected))

    def sample_graph(self) -> Graph:
        graph = InMemoryGraph()
        graph.add_property("id1", "rel1", "val11")
        graph.add_property_collection("id1", "rel2", {"val21", "val22"})
        graph.add_property("id1", "rel2", "val23")
        graph.add_meta_property("id1", "rdf:type", ":MyNode")
        graph.add_relation("id1", "connects", "id2")
        graph.add_meta_property("id2", "rdf:type", ":MyNode2")
        graph.add_meta_property("id2", "prop2", "val2")
        return graph
