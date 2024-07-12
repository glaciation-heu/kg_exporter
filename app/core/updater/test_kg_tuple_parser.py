from unittest import TestCase

from app.core.updater.kg_tuple_parser import KGTupleParser
from app.kg.inmemory_graph import InMemoryGraph


class KGTupleParserTest(TestCase):
    def test_parse_empty(self) -> None:
        parser = KGTupleParser()
        graph = parser.parse([])
        self.assertEqual(graph, InMemoryGraph())
