import asyncio

from loguru import logger
from prometheus_client import Counter
from pydantic_settings import BaseSettings

from app.clients.k8s.k8s_client import K8SClient
from app.core.async_queue import AsyncQueue
from app.core.builder.kg_slice_assembler import KGSliceAssembler
from app.core.builder.slice_strategy.slice_per_cluster import SlicePerCluster
from app.core.builder.slice_strategy.slice_per_node import SlicePerNode
from app.core.builder.slice_strategy.slice_strategy import SliceStrategy
from app.core.k8s_updates.k8s_update_pool import K8SUpdatePool
from app.core.kg.kg_repository import KGRepository
from app.core.repository.metric_repository import MetricRepository
from app.core.repository.query_settings import QuerySettings
from app.core.types import DKGSlice
from app.util.clock import Clock


class KGBuilderSettings(BaseSettings):
    builder_tick_seconds: int
    node_port: int
    is_single_slice: bool
    single_slice_url: str
    queries: QuerySettings


class KGBuilder:
    terminated: asyncio.Event
    k8s_client: K8SClient
    queue: AsyncQueue[DKGSlice]
    kg_repository: KGRepository
    influxdb_repository: MetricRepository
    k8s_pool: K8SUpdatePool
    settings: KGBuilderSettings
    slice_strategy: SliceStrategy
    slice_assembler: KGSliceAssembler
    errors_metric: Counter = Counter(
        "builder_errors_total", "knowledge graph builder errors"
    )
    successes_metric: Counter = Counter(
        "builder_successes_total", "knowledge graph builder successes"
    )
    passes_metric: Counter = Counter(
        "builder_cycles_total", "knowledge graph builder cycles"
    )

    def __init__(
        self,
        terminated: asyncio.Event,
        clock: Clock,
        queue: AsyncQueue[DKGSlice],
        k8s_client: K8SClient,
        kg_repository: KGRepository,
        metric_repository: MetricRepository,
        k8s_pool: K8SUpdatePool,
        settings: KGBuilderSettings,
    ):
        self.terminated = terminated
        self.clock = clock
        self.k8s_client = k8s_client
        self.queue = queue
        self.kg_repository = kg_repository
        self.metric_repository = metric_repository
        self.k8s_pool = k8s_pool
        self.settings = settings
        self.slice_strategy = (
            SlicePerCluster(settings.single_slice_url)
            if settings.is_single_slice
            else SlicePerNode(node_port=settings.node_port)
        )
        self.slice_assembler = KGSliceAssembler()

    async def run(self) -> None:
        logger.info("Builder started.")
        while not self.terminated.is_set():
            now_seconds = self.clock.now_seconds()

            try:
                self.passes_metric.inc()
                await self.run_cycle(now_seconds)
                self.successes_metric.inc()
            except Exception as e:
                logger.error(f"Builder error: {type(e)}, {e}")
                self.errors_metric.inc()

            sleep_seconds = (
                now_seconds
                + self.settings.builder_tick_seconds
                - self.clock.now_seconds()
            )
            if sleep_seconds > 0:
                await asyncio.sleep(sleep_seconds)

        logger.info("Builder stopped.")

    async def run_cycle(self, now_seconds: int) -> None:
        now = now_seconds * 1000
        (cluster_snapshot, metric_snapshot) = await asyncio.gather(
            self.k8s_client.fetch_snapshot(),
            self.metric_repository.metric_snapshot(now, self.settings.queries),
        )

        terminated_pods = self.k8s_pool.drain_terminated()
        cluster_snapshot.pods.extend(terminated_pods)

        logger.debug("Cluster snapshot: {size}", size=len(cluster_snapshot.cluster))
        logger.debug("Nodes: {size}", size=len(cluster_snapshot.nodes))
        logger.debug("Pods: {size}", size=len(cluster_snapshot.pods))
        logger.debug("Terminated Pods: {size}", size=len(terminated_pods))
        logger.debug("Deployments: {size}", size=len(cluster_snapshot.deployments))
        logger.debug("ReplicaSets: {size}", size=len(cluster_snapshot.replicasets))
        logger.debug("DaemonSets: {size}", size=len(cluster_snapshot.daemonsets))
        logger.debug("StatefullSets: {size}", size=len(cluster_snapshot.statefullsets))
        logger.debug("Jobs: {size}", size=len(cluster_snapshot.jobs))
        logger.debug("NodeMetrics: {size}", size=len(metric_snapshot.node_metrics))
        logger.debug("PodMetrics: {size}", size=len(metric_snapshot.pod_metrics))

        slices = self.slice_strategy.get_slices(cluster_snapshot, metric_snapshot)

        logger.info("Slices produced: {size}", size=len(slices))
        logger.debug("Slices: {slices}", slices=set(slices.keys()))
        for slice_id, slice_inputs in slices.items():
            existing_metadata = await self.kg_repository.query_snapshot(slice_id)
            logger.debug("Assembling slice: {slice_id}", slice_id=slice_id)
            slice = self.slice_assembler.assemble(
                now=now,
                slice_id=slice_id,
                inputs=slice_inputs,
                existing_metadata=existing_metadata,
            )
            self.queue.put_nowait(slice)
