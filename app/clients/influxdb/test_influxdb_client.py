import asyncio
from unittest import TestCase


class InfluxDBClientTest(TestCase):
    loop: asyncio.AbstractEventLoop

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.maxDiff = None

    def test_integration(self):
        pass
