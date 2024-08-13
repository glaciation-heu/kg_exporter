import asyncio

from loguru import logger
from prometheus_client import Counter

from app.core.async_queue import AsyncQueue
from app.core.dkg_slice_store import DKGSliceStore
from app.core.kg.kg_repository import KGRepository
from app.core.types import DKGSlice


class KGUpdater:
    queue: AsyncQueue[DKGSlice]
    kg_repository: KGRepository
    terminated: asyncio.Event
    slices: DKGSliceStore
    errors_metric: Counter = Counter(
        "updater_errors_total", "knowledge graph updater errors"
    )
    successes_metric: Counter = Counter(
        "updater_successes_total", "knowledge graph updater successes"
    )
    passes_metric: Counter = Counter(
        "updater_cycles_total", "knowledge graph updater cycles"
    )
    updates_metric: Counter = Counter(
        "updater_updates_total", "knowledge graph updates"
    )

    def __init__(
        self,
        terminated: asyncio.Event,
        queue: AsyncQueue[DKGSlice],
        kg_repository: KGRepository,
    ):
        self.queue = queue
        self.kg_repository = kg_repository
        self.terminated = terminated
        self.slices = DKGSliceStore()

    async def run(self) -> None:
        logger.info("Updater started.")
        while not self.terminated.is_set():
            try:
                self.passes_metric.inc()
                await self.run_cycle()
                self.successes_metric.inc()
            except Exception as e:
                self.errors_metric.inc()
                logger.error(f"Updater error: {e}")
        logger.info("Updater stopped.")

    async def run_cycle(self) -> None:
        slice = self.queue.get_nowait()
        if slice:
            to_update = self.slices.update(slice)
            if to_update:
                logger.info(
                    "updating slice {slice}, with timestamp {timestamp}",
                    slice=slice.slice_id,
                    timestamp=slice.timestamp,
                )
                await self.kg_repository.update(
                    slice.slice_id, slice.graph, slice.context
                )
                self.updates_metric.inc()
        else:
            await asyncio.sleep(0.5)
