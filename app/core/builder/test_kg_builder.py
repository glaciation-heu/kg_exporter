import asyncio
import datetime
from unittest import TestCase

from app.clients.influxdb.mock_infuxdbclient import MockInfluxDBClient
from app.clients.k8s.mock_k8s_client import MockK8SClient
from app.clients.metadata_service.mock_metadata_service_client import (
    MockMetadataServiceClient,
)
from app.core.async_queue import AsyncQueue
from app.core.builder.kg_builder import KGBuilder, KGBuilderSettings, QuerySettings
from app.core.repository.metric_repository import MetricRepository
from app.core.test_graph_fixture import TestGraphFixture
from app.core.test_snapshot_base import SnapshotTestBase
from app.core.types import DKGSlice, KGSliceId
from app.core.updater.kg_repository import KGRepository
from app.kg.inmemory_graph import InMemoryGraph
from app.util.clock import Clock
from app.util.mock_clock import MockClock


class KGBuilderTest(TestCase, TestGraphFixture, SnapshotTestBase):
    clock: Clock
    client: MockMetadataServiceClient
    k8s_client: MockK8SClient
    influxdb_client: MockInfluxDBClient
    queue: AsyncQueue[DKGSlice]
    running_event: asyncio.Event
    runner: asyncio.Runner
    settings: KGBuilderSettings

    def setUp(self) -> None:
        self.maxDiff = None
        self.clock = MockClock()
        self.client = MockMetadataServiceClient()
        self.influxdb_client = MockInfluxDBClient()
        self.queue = AsyncQueue()
        self.k8s_client = MockK8SClient()
        self.running_event = asyncio.Event()
        self.runner = asyncio.Runner()
        self.settings = KGBuilderSettings(
            builder_tick_seconds=1,
            node_port=80,
            queries=QuerySettings(),
            is_single_slice=False,
            single_slice_url="test",
        )

    def test_build_minimal(self) -> None:
        self.mock_inputs(
            "minimal", self.k8s_client, self.influxdb_client, self.settings.queries
        )

        builder = self.create_builder()
        self.runner.run(self.run_builder(builder))

        slice = self.wait_for_slice(2)

        self.assertEqual(slice.timestamp, 1000)
        self.assertEqual(slice.slice_id, KGSliceId("glaciation-test-master01", 80))
        self.assertNotEqual(slice.graph, InMemoryGraph())
        self.assert_graph(slice.graph, "minimal", slice.slice_id)

    def create_builder(self) -> KGBuilder:
        repository = KGRepository(self.client)
        influxdb_repository = MetricRepository(self.influxdb_client)
        return KGBuilder(
            self.running_event,
            self.clock,
            self.queue,
            self.k8s_client,
            repository,
            influxdb_repository,
            self.settings,
        )

    def wait_for_slice(self, seconds: int) -> DKGSlice:
        start = datetime.datetime.now()
        while start + datetime.timedelta(seconds=seconds) > datetime.datetime.now():
            slice = self.queue.get_nowait()
            if slice:
                return slice
            self.runner.run(asyncio.sleep(0.1))
        raise AssertionError("time is up.")

    async def run_builder(self, builder: KGBuilder) -> None:
        asyncio.create_task(builder.run())
