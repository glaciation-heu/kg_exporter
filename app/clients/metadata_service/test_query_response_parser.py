import json
import unittest

from app.clients.metadata_service.query_response_parser import QueryResponseParser
from app.kg.iri import IRI
from app.kg.literal import Literal


class QueryResponseParserTest(unittest.TestCase):
    EMPTY = json.dumps({"head": {"vars": []}, "results": {"bindings": []}})

    BASIC = json.dumps(
        {
            "head": {"vars": ["sub", "pred", "obj"]},
            "results": {
                "bindings": [
                    {
                        "obj": {
                            "type": "uri",
                            "value": "http://data.kasabi.com/dataset/cheese/schema/Cheese",
                        },
                        "pred": {
                            "type": "uri",
                            "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                        },
                        "sub": {
                            "type": "uri",
                            "value": "http://data.kasabi.com/dataset/cheese/halloumi",
                        },
                    },
                    {
                        "obj": {
                            "type": "literal",
                            "value": "Halloumi",
                            "xml:lang": "el",
                        },
                        "pred": {
                            "type": "uri",
                            "value": "http://www.w3.org/2000/01/rdf-schema#label",
                        },
                        "sub": {
                            "type": "uri",
                            "value": "http://data.kasabi.com/dataset/cheese/halloumi",
                        },
                    },
                    {
                        "obj": {"type": "literal", "value": "Halloumi"},
                        "pred": {
                            "type": "uri",
                            "value": "glc:property",
                        },
                        "sub": {
                            "type": "uri",
                            "value": "https://kubernetes.local/kafka.kafka-broker-1.kafka-init.Status",
                        },
                    },
                ]
            },
        }
    )

    def test_parse_empty(self) -> None:
        parser = QueryResponseParser()
        results = parser.parse(self.EMPTY)
        self.assertEqual([], results)

    def test_single_type(self) -> None:
        parser = QueryResponseParser()
        results = parser.parse(self.BASIC)
        self.assertEqual(
            results,
            [
                {
                    "obj": IRI(
                        "http://data.kasabi.com/dataset/cheese/schema/", "Cheese"
                    ),
                    "pred": IRI("http://www.w3.org/1999/02/22-rdf-syntax-ns", "type"),
                    "sub": IRI("http://data.kasabi.com/dataset/cheese/", "halloumi"),
                },
                {
                    "obj": Literal("Halloumi", Literal.TYPE_STRING),
                    "pred": IRI("http://www.w3.org/2000/01/rdf-schema", "label"),
                    "sub": IRI("http://data.kasabi.com/dataset/cheese/", "halloumi"),
                },
                {
                    "obj": Literal("Halloumi", Literal.TYPE_STRING),
                    "pred": IRI("glc", "property"),
                    "sub": IRI(
                        "https://kubernetes.local/",
                        "kafka.kafka-broker-1.kafka-init.Status",
                    ),
                },
            ],
        )
