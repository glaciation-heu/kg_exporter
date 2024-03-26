import json
from io import StringIO
from unittest import TestCase

from app.kg.graph import Graph
from app.kg.inmemory_graph import InMemoryGraph
from app.kg.iri import IRI
from app.kg.literal import Literal
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
        graph.add_meta_property(
            IRI("pref", "id1"), Graph.RDF_TYPE_IRI, IRI("pref", "MyNode")
        )
        configs = JsonLDConfiguration(dict(), set())
        with self.assertRaises(Exception) as e:
            JsonLDSerialializer(configs).write(buffer, graph)
        self.assertEqual(
            str(e.exception), "Prefix for pref:MyNode cannot be found in any context."
        )

    def test_simple_node(self):
        buffer = StringIO()
        graph = InMemoryGraph()
        graph.add_meta_property(
            IRI("pref", "id1"), Graph.RDF_TYPE_IRI, IRI("pref", "MyNode")
        )
        configs = JsonLDConfiguration(
            {JsonLDConfiguration.DEFAULT_CONTEXT_IRI: {"pref": "whatever"}}, set()
        )
        JsonLDSerialializer(configs).write(buffer, graph)
        self.assertEqual(
            buffer.getvalue(),
            json.dumps(
                {
                    "@context": {"pref": "whatever"},
                    "@graph": [{"@id": "pref:id1", "@type": "pref:MyNode"}],
                }
            ),
        )

    def test_two_nodes(self):
        buffer = StringIO()
        configs = JsonLDConfiguration(
            {
                IRI("pref", "MyNode"): {
                    "pref": "http://example.com/",
                    "MyNode": "http://example.com/MyNode",
                    "rel1": "http://example.com/MyNode/rel1",
                    "rel2": "http://example.com/MyNode/rel2",
                    "connects": "http://example.com/MyNode/connects",
                },
                IRI("pref", "MyNode2"): {
                    "pref": "http://example.com/",
                    "prop2": "http://example.com/MyNode2/prop2",
                    "MyNode2": "http://example.com/MyNode2",
                },
            },
            {IRI("pref", "MyNode2")},
        )
        JsonLDSerialializer(configs).write(buffer, self.sample_graph())

        expected = {
            "@graph": [
                {
                    "@id": "pref:id2",
                    "@type": "pref:MyNode2",
                    "@context": {
                        "pref": "http://example.com/",
                        "prop2": "http://example.com/MyNode2/prop2",
                        "MyNode2": "http://example.com/MyNode2",
                    },
                    "pref:prop2": "val2",
                },
                {
                    "@id": "pref:id1",
                    "@type": "pref:MyNode",
                    "@context": {
                        "pref": "http://example.com/",
                        "MyNode": "http://example.com/MyNode",
                        "rel1": "http://example.com/MyNode/rel1",
                        "rel2": "http://example.com/MyNode/rel2",
                        "connects": "http://example.com/MyNode/connects",
                    },
                    "pref:rel1": "val11",
                    "pref:rel2": {"@set": ["val21", "val22", "val23"]},
                    "pref:connects": "pref:id2",
                },
            ]
        }
        self.assertEqual(buffer.getvalue(), json.dumps(expected))

    def test_aggregates(self):
        buffer = StringIO()
        configs = JsonLDConfiguration(
            {
                IRI("pref", "MyNode"): {
                    "@vocab": "http://example.com/nodes",
                },
                IRI("pref", "Embedded"): {
                    "@vocab": "http://example.com/nodes",
                },
                IRI("pref", "Embedded2"): {
                    "@vocab": "http://example.com/nodes",
                },
                JsonLDConfiguration.DEFAULT_CONTEXT_IRI: {
                    "pref": "http://example.com/"
                },
            },
            {IRI("pref", "MyNode")},
        )

        graph = InMemoryGraph()
        graph.add_property(IRI("pref", "id1"), IRI("pref", "p1"), Literal("v1", "str"))
        graph.add_meta_property(
            IRI("pref", "id1"), Graph.RDF_TYPE_IRI, IRI("pref", "MyNode")
        )
        graph.add_relation(
            IRI("pref", "id1"), IRI("pref", "includes1"), IRI("pref", "id2")
        )
        graph.add_meta_property(
            IRI("pref", "id2"), Graph.RDF_TYPE_IRI, IRI("pref", "Embedded")
        )
        graph.add_meta_property(
            IRI("pref", "id2"), IRI("pref", "p2"), Literal("v2", "str")
        )
        graph.add_relation(
            IRI("pref", "id2"), IRI("pref", "includes2"), IRI("pref", "id3")
        )
        graph.add_meta_property(
            IRI("pref", "id3"), Graph.RDF_TYPE_IRI, IRI("pref", "Embedded2")
        )
        graph.add_meta_property(
            IRI("pref", "id3"), IRI("pref", "p3"), Literal("v3", "str")
        )

        JsonLDSerialializer(configs).write(buffer, graph)
        expected = {
            "@context": {"pref": "http://example.com/"},
            "@graph": [
                {
                    "@id": "pref:id1",
                    "@type": "pref:MyNode",
                    "@context": {"@vocab": "http://example.com/nodes"},
                    "pref:p1": "v1",
                    "pref:includes1": {
                        "@id": "pref:id2",
                        "@type": "pref:Embedded",
                        "@context": {"@vocab": "http://example.com/nodes"},
                        "pref:p2": "v2",
                        "pref:includes2": {
                            "@id": "pref:id3",
                            "@type": "pref:Embedded2",
                            "@context": {"@vocab": "http://example.com/nodes"},
                            "pref:p3": "v3",
                        },
                    },
                }
            ],
        }
        self.assertEqual(buffer.getvalue(), json.dumps(expected))

    def test_default_context(self):
        buffer = StringIO()
        configs = JsonLDConfiguration(
            {
                JsonLDConfiguration.DEFAULT_CONTEXT_IRI: {
                    "@vocab": "http://example.com/nodes",
                    "pref": "http://example.com/",
                },
            },
            set(),
        )

        graph = InMemoryGraph()
        graph.add_property(IRI("pref", "id1"), IRI("pref", "p1"), Literal("v1", "str"))
        graph.add_meta_property(
            IRI("pref", "id1"), Graph.RDF_TYPE_IRI, IRI("pref", "MyNode")
        )

        JsonLDSerialializer(configs).write(buffer, graph)
        expected = {
            "@context": {
                "@vocab": "http://example.com/nodes",
                "pref": "http://example.com/",
            },
            "@graph": [{"@id": "pref:id1", "@type": "pref:MyNode", "pref:p1": "v1"}],
        }
        self.assertEqual(buffer.getvalue(), json.dumps(expected))

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
            IRI("pref", "id1"), Graph.RDF_TYPE_IRI, IRI("pref", "MyNode")
        )
        graph.add_relation(
            IRI("pref", "id1"), IRI("pref", "connects"), IRI("pref", "id2")
        )
        graph.add_meta_property(
            IRI("pref", "id2"), Graph.RDF_TYPE_IRI, IRI("pref", "MyNode2")
        )
        graph.add_meta_property(
            IRI("pref", "id2"), IRI("pref", "prop2"), Literal("val2", "str")
        )
        return graph
