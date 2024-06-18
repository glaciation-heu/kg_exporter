import asyncio

from loguru import logger

from app.core.async_queue import AsyncQueue
from app.core.dkg_slice_store import DKGSliceStore
from app.core.kg_repository import KGRepository
from app.core.types import DKGSlice


class KGUpdater:
    queue: AsyncQueue[DKGSlice]
    kg_repository: KGRepository
    terminated: asyncio.Event
    slices: DKGSliceStore

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
                await self.run_cycle()
            except Exception as e:
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
                await self.kg_repository.update(slice.slice_id, slice.graph)
        else:
            await asyncio.sleep(0.5)
