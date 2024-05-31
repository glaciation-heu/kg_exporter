import asyncio
from unittest import TestCase

from app.core.async_queue import AsyncQueue


class AsyncQueueTest(TestCase):
    def test_nowait(self) -> None:
        queue = AsyncQueue[int]()
        self.assertEqual(None, queue.get_nowait())
        queue.put_nowait(1)
        queue.put_nowait(2)
        self.assertEqual(1, queue.get_nowait())
        self.assertEqual(2, queue.get_nowait())
        self.assertEqual(None, queue.get_nowait())

    def test_wait(self) -> None:
        runner = asyncio.Runner()
        queue = AsyncQueue[int]()
        queue.put_nowait(1)
        queue.put_nowait(2)
        self.assertEqual(1, runner.run(queue.get()))
        self.assertEqual(2, runner.run(queue.get()))
