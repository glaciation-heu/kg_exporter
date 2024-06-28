from typing import Any, List

import asyncio
from wsgiref.simple_server import WSGIServer

from loguru import logger
from prometheus_client import start_http_server

from app.clients.influxdb.metricstore_client import MetricStoreClient
from app.clients.k8s.k8s_client import K8SClient
from app.clients.metadata_service.metadata_service_client import MetadataServiceClient
from app.core.async_queue import AsyncQueue
from app.core.builder.kg_builder import KGBuilder
from app.core.kg_repository import KGRepository
from app.core.kg_updater import KGUpdater
from app.core.metric_repository import MetricRepository
from app.core.types import DKGSlice
from app.kgexporter_settings import KGExporterSettings
from app.util.clock import Clock


class KGExporterContext:
    builder: KGBuilder
    updater: KGUpdater
    queue: AsyncQueue[DKGSlice]
    runner: asyncio.Runner
    terminated: asyncio.Event
    prometheus_server: WSGIServer
    tasks: List[asyncio.Task[Any]]
    settings: KGExporterSettings

    def __init__(
        self,
        clock: Clock,
        metadata_client: MetadataServiceClient,
        k8s_client: K8SClient,
        metric_store_client: MetricStoreClient,
        settings: KGExporterSettings,
    ):
        self.settings = settings
        kg_repository = KGRepository(metadata_client)
        influxdb_repository = MetricRepository(metric_store_client)
        self.terminated = asyncio.Event()
        self.queue = AsyncQueue[DKGSlice]()
        self.builder = KGBuilder(
            self.terminated,
            clock,
            self.queue,
            k8s_client,
            kg_repository,
            influxdb_repository,
            self.settings.builder,
        )
        self.updater = KGUpdater(self.terminated, self.queue, kg_repository)
        self.runner = asyncio.Runner()
        self.tasks = []

    def start(self) -> None:
        if self.terminated.is_set():
            return
        self.terminated.clear()
        self.runner.run(self.run_tasks())
        server, _ = start_http_server(self.settings.prometheus.endpoint_port)
        self.prometheus_server = server

    async def run_tasks(self) -> None:
        self.tasks.append(asyncio.create_task(self.builder.run()))
        self.tasks.append(asyncio.create_task(self.updater.run()))

    def stop(self) -> None:
        self.terminated.set()
        self.prometheus_server.shutdown()

    def wait_for_termination(self) -> None:
        self.runner.run(self.terminated.wait())
        logger.info("Application terminated.")

    def exit_gracefully(self, _1: Any, _2: Any) -> None:
        self.stop()
        self.wait_for_termination()
