from typing import Any, Dict, List

import asyncio
import dataclasses
from unittest import TestCase

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.clients.k8s.mock_k8s_client import MockK8SClient


@dataclasses.dataclass
class TestClass:
    value: List[Dict[str, Any]]
    value2: List[Dict[str, Any]]


class K8SClientTest(TestCase):
    loop: asyncio.AbstractEventLoop

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.maxDiff = None

    def test_get_resource_snapshot(self):
        client = MockK8SClient()
        client.mock_daemonsets([{"daemonsets": "fake"}])
        client.mock_deployments([{"deployments": "fake"}])
        client.mock_jobs([{"jobs": "fake"}])
        client.mock_nodes([{"nodes": "fake"}])
        client.mock_pods([{"pods": "fake"}])
        client.mock_replicasets([{"replicasets": "fake"}])
        client.mock_statefullsets([{"statefullsets": "fake"}])
        actual = asyncio.run(client.fetch_snapshot())

        expected = ResourceSnapshot(
            pods=[{"pods": "fake"}],
            nodes=[{"nodes": "fake"}],
            deployments=[{"deployments": "fake"}],
            jobs=[{"jobs": "fake"}],
            statefullsets=[{"statefullsets": "fake"}],
            daemonsets=[{"daemonsets": "fake"}],
            replicasets=[{"replicasets": "fake"}],
        )
        self.assertEqual(expected, actual)
