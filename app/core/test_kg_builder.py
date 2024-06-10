import asyncio
import datetime
from unittest import TestCase

from app.clients.influxdb.mock_infuxdbclient import MockInfluxDBClient
from app.clients.k8s.mock_k8s_client import MockK8SClient
from app.clients.metadata_service.mock_metadata_service_client import (
    MockMetadataServiceClient,
)
from app.core.async_queue import AsyncQueue
from app.core.kg_builder import KGBuilder, KGBuilderSettings, QuerySettings
from app.core.kg_repository import KGRepository
from app.core.metric_repository import MetricRepository
from app.core.test_graph_fixture import TestGraphFixture
from app.core.types import DKGSlice, KGSliceId
from app.kg.inmemory_graph import InMemoryGraph


class KGBuilderTest(TestCase, TestGraphFixture):
    client: MockMetadataServiceClient
    k8s_client: MockK8SClient
    influxdb_client: MockInfluxDBClient
    queue: AsyncQueue[DKGSlice]
    running_event: asyncio.Event
    runner: asyncio.Runner
    settings: KGBuilderSettings

    def setUp(self) -> None:
        self.client = MockMetadataServiceClient()
        self.influxdb_client = MockInfluxDBClient()
        self.queue = AsyncQueue()
        self.k8s_client = MockK8SClient()
        self.running_event = asyncio.Event()
        self.running_event.set()
        self.runner = asyncio.Runner()
        self.settings = KGBuilderSettings(
            builder_tick_seconds=1, influxdb_queries=QuerySettings()
        )

    def test_build(self) -> None:
        builder = self.create_builder()
        self.runner.run(self.run_builder(builder))

        slice = self.wait_for_slice(2)

        self.assertEqual(slice.graph, InMemoryGraph())
        self.assertEqual(slice.timestamp, 0)
        self.assertEqual(slice.slice_id, KGSliceId("127.0.0.1", 80))

    def wait_for_slice(self, seconds: int) -> DKGSlice:
        start = datetime.datetime.now()
        while start + datetime.timedelta(seconds=seconds) > datetime.datetime.now():
            slice = self.queue.get_nowait()
            if slice:
                return slice
            self.runner.run(asyncio.sleep(0.1))
        raise AssertionError("time is up.")

    def create_builder(self) -> KGBuilder:
        repository = KGRepository(self.client, self.get_jsonld_config())
        influxdb_repository = MetricRepository(self.influxdb_client)
        return KGBuilder(
            self.running_event,
            self.queue,
            self.k8s_client,
            repository,
            influxdb_repository,
            self.settings,
        )

    async def run_builder(self, builder: KGBuilder) -> None:
        asyncio.create_task(builder.run())
