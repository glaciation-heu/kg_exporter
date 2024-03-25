import json
from io import StringIO
from unittest import TestCase

from app.kg.graph import Graph
from app.kg.inmemory_graph import InMemoryGraph
from app.serialize.jsonld_configuration import JsonLDConfiguration
from app.serialize.jsonld_serializer import JsonLDSerialializer


class JsonLDSerializerTest(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_empty(self):
        buffer = StringIO()
        configs = JsonLDConfiguration(dict(), set())
        JsonLDSerialializer(configs).write(buffer, InMemoryGraph())
        self.assertEqual(buffer.getvalue(), json.dumps({"@graph": []}))

    def test_no_context(self):
        buffer = StringIO()
        graph = InMemoryGraph()
        graph.add_meta_property("id1", "rdf:type", ":MyNode")
        configs = JsonLDConfiguration(dict(), set())
        JsonLDSerialializer(configs).write(buffer, graph)
        expected = json.dumps({"@graph": [{"@id": "id1", "@type": ":MyNode"}]})
        self.assertEqual(buffer.getvalue(), expected)

    def test_two_nodes(self):
        buffer = StringIO()
        configs = JsonLDConfiguration(
            {
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
            },
            {":MyNode2"},
        )
        JsonLDSerialializer(configs).write(buffer, self.sample_graph())

        expected = {
            "@graph": [
                {
                    "@id": "id2",
                    "@type": ":MyNode2",
                    "@context": {
                        "prop2": "http://example.com/MyNode2/prop2",
                        "MyNode2": "http://example.com/MyNode2",
                    },
                    "prop2": "val2",
                },
                {
                    "@id": "id1",
                    "@type": ":MyNode",
                    "@context": {
                        "MyNode": "http://example.com/MyNode",
                        "rel1": "http://example.com/MyNode/rel1",
                        "rel2": "http://example.com/MyNode/rel2",
                        "connects": "http://example.com/MyNode/connects",
                    },
                    "rel1": "val11",
                    "rel2": {"@set": ["val21", "val22", "val23"]},
                    "connects": "id2",
                },
            ]
        }
        self.assertEqual(buffer.getvalue(), json.dumps(expected))

    def test_aggregates(self):
        buffer = StringIO()
        configs = JsonLDConfiguration(
            {
                ":MyNode": {
                    "@vocab": "http://example.com/nodes",
                },
                ":Embedded": {
                    "@vocab": "http://example.com/nodes",
                },
                ":Embedded2": {
                    "@vocab": "http://example.com/nodes",
                },
            },
            {":MyNode"},
        )

        graph = InMemoryGraph()
        graph.add_property("id1", "p1", "v1")
        graph.add_meta_property("id1", "rdf:type", ":MyNode")
        graph.add_relation("id1", "includes1", "id2")
        graph.add_meta_property("id2", "rdf:type", ":Embedded")
        graph.add_meta_property("id2", "p2", "v2")
        graph.add_relation("id2", "includes2", "id3")
        graph.add_meta_property("id3", "rdf:type", ":Embedded2")
        graph.add_meta_property("id3", "p3", "v3")

        JsonLDSerialializer(configs).write(buffer, graph)
        expected = {
            "@graph": [
                {
                    "@id": "id1",
                    "@type": ":MyNode",
                    "@context": {"@vocab": "http://example.com/nodes"},
                    "p1": "v1",
                    "includes1": {
                        "@id": "id2",
                        "@type": ":Embedded",
                        "@context": {"@vocab": "http://example.com/nodes"},
                        "p2": "v2",
                        "includes2": {
                            "@id": "id3",
                            "@type": ":Embedded2",
                            "@context": {"@vocab": "http://example.com/nodes"},
                            "p3": "v3",
                        },
                    },
                }
            ]
        }
        self.assertEqual(buffer.getvalue(), json.dumps(expected))

    def test_default_context(self):
        buffer = StringIO()
        configs = JsonLDConfiguration(
            {
                "__default__": {
                    "@vocab": "http://example.com/nodes",
                },
            },
            set(),
        )

        graph = InMemoryGraph()
        graph.add_property("id1", "p1", "v1")
        graph.add_meta_property("id1", "rdf:type", ":MyNode")

        JsonLDSerialializer(configs).write(buffer, graph)
        expected = {
            "@context": {"@vocab": "http://example.com/nodes"},
            "@graph": [{"@id": "id1", "@type": ":MyNode", "p1": "v1"}],
        }
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
