import asyncio
from unittest import TestCase

from app.clients.metadata_service.mock_metadata_service_client import (
    MockMetadataServiceClient,
)
from app.core.kg.kg_repository import KGRepository
from app.core.kg.resource_status_query import (
    ResourceStatus,
    ResourceStatusQuery,
    ResourceType,
)
from app.core.test_graph_fixture import TestGraphFixture
from app.core.types import KGSliceId
from app.kg.iri import IRI
from app.kg.literal import Literal


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
        query = ResourceStatusQuery(ResourceType.POD)

        client.mock_query(
            slice_id.get_host_port(),
            query.get_query(),
            [
                {
                    "resource": IRI("prefix", "id"),
                    "statusValue": Literal("running", Literal.TYPE_STRING),
                }
            ],
        )

        actual = asyncio.run(repository.query(slice_id, query))

        self.assertEqual(
            [ResourceStatus(IRI("prefix", "id"), "running", ResourceType.POD)], actual
        )
