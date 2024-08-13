import asyncio
import datetime
from unittest import TestCase

from app.clients.metadata_service.mock_metadata_service_client import (
    MockMetadataServiceClient,
    SerializedGraph,
)
from app.core.async_queue import AsyncQueue
from app.core.kg.kg_repository import KGRepository
from app.core.test_graph_fixture import TestGraphFixture
from app.core.types import DKGSlice, KGSliceId
from app.core.updater.kg_updater import KGUpdater


class KGUpdaterTest(TestCase, TestGraphFixture):
    client: MockMetadataServiceClient
    queue: AsyncQueue[DKGSlice]
    running_event: asyncio.Event
    runner: asyncio.Runner

    def setUp(self) -> None:
        self.client = MockMetadataServiceClient()
        self.queue = AsyncQueue()
        self.running_event = asyncio.Event()
        self.runner = asyncio.Runner()

    def test_kg_updater(self) -> None:
        updater = self.create_updater()
        self.runner.run(self.run_updater(updater))

        graph, serialized = self.simple_node()
        slice_id = KGSliceId("127.0.0.1", 80)
        slice = DKGSlice(slice_id, graph, self.get_test_context(), 1)
        self.queue.put_nowait(slice)

        graph_str = self.wait_for_graph(slice_id, 5)
        self.assertEqual(serialized, graph_str)

        self.running_event.clear()

    def wait_for_graph(self, slice_id: KGSliceId, seconds: int) -> SerializedGraph:
        start = datetime.datetime.now()
        while start + datetime.timedelta(seconds=seconds) > datetime.datetime.now():
            graphs = self.client.take_inserts(slice_id.get_host_port())
            if len(graphs) > 0:
                return graphs[0]
            self.runner.run(asyncio.sleep(0.1))
        raise AssertionError("time is up.")

    def create_updater(self) -> KGUpdater:
        repository = KGRepository(self.client)
        return KGUpdater(self.running_event, self.queue, repository)

    async def run_updater(self, updater: KGUpdater) -> None:
        asyncio.create_task(updater.run())
