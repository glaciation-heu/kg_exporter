from typing import List

import asyncio

from loguru import logger
from pydantic_settings import BaseSettings

from app.clients.k8s.k8s_client import K8SClient
from app.core.async_queue import AsyncQueue
from app.core.influxdb_repository import InfluxDBRepository, MetricQuery
from app.core.kg_repository import KGRepository
from app.core.kg_slice_assembler import KGSliceAssembler
from app.core.slice_for_node_strategy import SliceForNodeStrategy
from app.core.slice_strategy import SliceStrategy
from app.core.types import DKGSlice, MetricSnapshot


class QuerySettings(BaseSettings):
    pod_queries: List[MetricQuery] = []
    node_queries: List[MetricQuery] = []
    workload_queries: List[MetricQuery] = []


class KGBuilderSettings(BaseSettings):
    builder_tick_seconds: int
    influxdb_queries: QuerySettings


class KGBuilder:
    running: asyncio.Event
    k8s_client: K8SClient
    queue: AsyncQueue[DKGSlice]
    kg_repository: KGRepository
    influxdb_repository: InfluxDBRepository
    settings: KGBuilderSettings
    slice_strategy: SliceStrategy
    slice_assembler: KGSliceAssembler

    def __init__(
        self,
        running: asyncio.Event,
        queue: AsyncQueue[DKGSlice],
        k8s_client: K8SClient,
        kg_repository: KGRepository,
        influxdb_repository: InfluxDBRepository,
        settings: KGBuilderSettings,
    ):
        self.running = running
        self.k8s_client = k8s_client
        self.queue = queue
        self.kg_repository = kg_repository
        self.influxdb_repository = influxdb_repository
        self.settings = settings
        self.slice_strategy = SliceForNodeStrategy()
        self.slice_assembler = KGSliceAssembler()

    async def run(self) -> None:
        while self.running.is_set():
            now = 0
            (
                cluster_snapshot,
                pod_metrics,
                node_metrics,
                workload_metrics,
            ) = await asyncio.gather(
                self.k8s_client.fetch_snapshot(),
                self.influxdb_repository.query_many(
                    now, self.settings.influxdb_queries.pod_queries
                ),
                self.influxdb_repository.query_many(
                    now, self.settings.influxdb_queries.node_queries
                ),
                self.influxdb_repository.query_many(
                    now, self.settings.influxdb_queries.workload_queries
                ),
            )
            metric_snapshot = MetricSnapshot(
                pod_metrics, node_metrics, workload_metrics
            )
            logger.debug(cluster_snapshot)
            logger.debug(pod_metrics)
            logger.debug(node_metrics)
            logger.debug(workload_metrics)

            slices = self.slice_strategy.get_slices(cluster_snapshot, metric_snapshot)
            for slice_id, slice_inputs in slices.items():
                slice = self.slice_assembler.assemble(
                    now=now, slice_id=slice_id, inputs=slice_inputs
                )
                self.queue.put_nowait(slice)
            await asyncio.sleep(30)
