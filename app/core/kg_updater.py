import asyncio

from loguru import logger

from app.core.async_queue import AsyncQueue
from app.core.kg_repository import KGRepository
from app.core.types import DKGSlice


class KGUpdater:
    queue: AsyncQueue[DKGSlice]
    kg_repository: KGRepository
    running: asyncio.Event

    def __init__(
        self,
        running: asyncio.Event,
        queue: AsyncQueue[DKGSlice],
        kg_repository: KGRepository,
    ):
        self.queue = queue
        self.kg_repository = kg_repository
        self.running = running

    async def run(self) -> None:
        while self.running.is_set():
            slice = self.queue.get_nowait()
            if slice:
                logger.debug(
                    "updating slice {slice}, with timestamp {timestamp}",
                    slice=slice.slice_id,
                    timestamp=slice.timestamp,
                )
                await self.kg_repository.update(slice.slice_id, slice.graph)
            else:
                await asyncio.sleep(0.3)
