from typing import Generic, Optional, TypeVar

import asyncio

T = TypeVar("T")


class AsyncQueue(Generic[T]):
    elements: asyncio.Queue[T]

    def __init__(self):
        self.elements = asyncio.Queue()

    def get_nowait(self) -> Optional[T]:
        try:
            return self.elements.get_nowait()
        except asyncio.QueueEmpty:
            return None

    def put_nowait(self, element: T) -> None:
        self.elements.put_nowait(element)

    async def get(self) -> T:
        return await self.elements.get()

    async def put(self, element: T) -> None:
        await self.elements.put(element)
