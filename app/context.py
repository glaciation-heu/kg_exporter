from typing import Any, List

import asyncio

from app.clients.influxdb.influxdb_client import InfluxDBClient
from app.clients.k8s.k8s_client import K8SClient
from app.clients.metadata_service.metadata_service_client import MetadataServiceClient
from app.core.async_queue import AsyncQueue
from app.core.dkg_slice_store import DKGSliceStore
from app.core.influxdb_repository import InfluxDBRepository
from app.core.kg_builder import KGBuilder
from app.core.kg_repository import KGRepository
from app.core.kg_updater import KGUpdater
from app.core.types import DKGSlice
from app.serialize.jsonld_configuration import JsonLDConfiguration


class KGExporterContext:
    builder: KGBuilder
    updater: KGUpdater
    queue: AsyncQueue[DKGSlice]
    runner: asyncio.Runner
    dkg_slice_store: DKGSliceStore
    running: asyncio.Event
    tasks: List[asyncio.Task[Any]]

    def __init__(
        self,
        metadata_client: MetadataServiceClient,
        k8s_client: K8SClient,
        influxdb_client: InfluxDBClient,
        jsonld_config: JsonLDConfiguration,
    ):
        kg_repository = KGRepository(metadata_client, jsonld_config)
        influxdb_repository = InfluxDBRepository(influxdb_client)
        self.running = asyncio.Event()
        self.queue = AsyncQueue[DKGSlice]()
        self.dkg_slice_store = DKGSliceStore()
        self.builder = KGBuilder(
            self.running,
            self.queue,
            k8s_client,
            kg_repository,
            influxdb_repository,
        )
        self.updater = KGUpdater(self.running, self.queue, kg_repository)
        self.runner = asyncio.Runner()
        self.tasks = []

    def start(self) -> None:
        if self.running.is_set():
            return
        self.running.set()
        self.runner.run(self.run_tasks())

    async def run_tasks(self) -> None:
        self.tasks.append(asyncio.create_task(self.builder.run()))
        self.tasks.append(asyncio.create_task(self.updater.run()))

    def stop(self) -> None:
        self.running.clear()
