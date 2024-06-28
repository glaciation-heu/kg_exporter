import asyncio
from unittest import TestCase

from app.clients.metadata_service.mock_metadata_service_client import (
    MockMetadataServiceClient,
)
from app.core.test_graph_fixture import TestGraphFixture
from app.core.types import KGSliceId
from app.core.updater.kg_repository import KGRepository
from app.core.updater.kg_tuple_parser import KGTupleParser
from app.kg.inmemory_graph import InMemoryGraph


class KGRepositoryTest(TestCase, TestGraphFixture):
    def test_update(self) -> None:
        client = MockMetadataServiceClient()
        repository = KGRepository(client)
        slice_id = KGSliceId("127.0.0.1", 80)

        graph, expected = self.simple_node()
        asyncio.run(repository.update(slice_id, graph, self.get_test_context()))

        graphs = client.take_inserts(slice_id.get_host_port())
        self.assertEqual(expected, graphs[0])

    def test_query(self) -> None:
        client = MockMetadataServiceClient()
        repository = KGRepository(client)
        slice_id = KGSliceId("127.0.0.1", 80)
        query_str = "sparql query"
        result_parser = KGTupleParser()

        client.mock_query(slice_id.get_host_port(), query_str, [])

        actual = asyncio.run(repository.query(slice_id, query_str, result_parser))
        expected = InMemoryGraph()
        self.assertEqual(expected, actual)
