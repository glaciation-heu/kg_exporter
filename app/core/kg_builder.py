import asyncio

from loguru import logger

from app.clients.k8s.k8s_client import K8SClient
from app.core.async_queue import AsyncQueue
from app.core.influxdb_repository import InfluxDBRepository
from app.core.kg_repository import KGRepository
from app.core.kg_slice_assembler import KGSliceAssembler
from app.core.slice_for_node_strategy import SliceForNodeStrategy
from app.core.slice_strategy import SliceStrategy
from app.core.types import DKGSlice, QueryOptions


class KGBuilder:
    running: asyncio.Event
    k8s_client: K8SClient
    queue: AsyncQueue[DKGSlice]
    kg_repository: KGRepository
    influxdb_repository: InfluxDBRepository
    query_options: QueryOptions
    slice_strategy: SliceStrategy
    slice_assembler: KGSliceAssembler

    def __init__(
        self,
        running: asyncio.Event,
        queue: AsyncQueue[DKGSlice],
        k8s_client: K8SClient,
        kg_repository: KGRepository,
        influxdb_repository: InfluxDBRepository,
    ):
        self.running = running
        self.k8s_client = k8s_client
        self.queue = queue
        self.kg_repository = kg_repository
        self.influxdb_repository = influxdb_repository
        self.query_options = QueryOptions(
            pod_queries=[], node_queries=[], workload_queries=[]
        )
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
                    now, self.query_options.pod_queries
                ),
                self.influxdb_repository.query_many(
                    now, self.query_options.node_queries
                ),
                self.influxdb_repository.query_many(
                    now, self.query_options.workload_queries
                ),
            )
            logger.debug(cluster_snapshot)
            logger.debug(pod_metrics)
            logger.debug(node_metrics)
            logger.debug(workload_metrics)

            slice_ids = self.slice_strategy.get_slices(cluster_snapshot)
            for slice_id in slice_ids:
                slice = self.slice_assembler.assemble(
                    now=now,
                    slice_id=slice_id,
                    cluster_snapshot=cluster_snapshot,
                    pod_metrics=pod_metrics,
                    node_metrics=node_metrics,
                    workload_metrics=workload_metrics,
                )
                self.queue.put_nowait(slice)
            await asyncio.sleep(30)
