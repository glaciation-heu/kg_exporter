from typing import Any, Dict, List

import asyncio
import datetime
from unittest import TestCase

from app.clients.k8s.k8s_event import EventType, K8SEvent, Kind
from app.clients.k8s.mock_k8s_client import MockK8SClient
from app.core.k8s_updates.k8s_update_pool_impl import K8SUpdatePoolImpl


class K8SUpdatePoolImplTest(TestCase):
    k8s_client: MockK8SClient
    tasks: List[asyncio.Task[Any]]
    loop: asyncio.AbstractEventLoop

    def setUp(self) -> None:
        self.loop = asyncio.get_event_loop()
        self.k8s_client = MockK8SClient()
        self.pool = K8SUpdatePoolImpl(self.k8s_client)
        self.tasks = []

    def tearDown(self) -> None:
        for task in self.tasks:
            task.cancel()

    def test_drain_empty(self) -> None:
        self.tasks.append(self.loop.create_task(self.pool.subscribe()))

        result = self.pool.drain_terminated()
        self.assertEqual(result, [])

    def test_drain_deleted_single(self) -> None:
        pod1 = {
            "metadata": {"name": "pod1", "namespace": "ns1"},
            "status": {"phase": "Running"},
        }
        pod2 = {
            "metadata": {"name": "pod2", "namespace": "ns1"},
            "status": {"phase": "Running"},
        }
        pod3 = {
            "metadata": {"name": "pod3", "namespace": "ns1"},
            "status": {"phase": "Running"},
        }
        events = [
            K8SEvent(event=EventType.ADDED, kind=Kind.POD, resource=pod1, version=1),
            K8SEvent(event=EventType.MODIFIED, kind=Kind.POD, resource=pod2, version=2),
            K8SEvent(event=EventType.DELETED, kind=Kind.POD, resource=pod3, version=3),
        ]
        self.k8s_client.mock_watched_pods(events)

        self.tasks.append(self.loop.create_task(self.pool.subscribe()))

        result = self.wait_for_result(2, 1)

        self.assertEqual(result, [pod3])
        self.assertEqual(result[0]["status"]["phase"], "Succeeded")

    def test_drain_last_update(self) -> None:
        pod1 = {
            "metadata": {"name": "pod1", "namespace": "ns1", "resourceVersion": 1},
            "status": {"phase": "Running"},
        }
        pod2 = {
            "metadata": {"name": "pod1", "namespace": "ns1", "resourceVersion": 2},
            "status": {"phase": "Running"},
        }
        pod3 = {
            "metadata": {"name": "pod1", "namespace": "ns1", "resourceVersion": 3},
            "status": {"phase": "Running"},
        }
        pod4 = {
            "metadata": {"name": "pod1", "namespace": "ns1", "resourceVersion": 4},
            "status": {"phase": "Running"},
        }
        events = [
            K8SEvent(event=EventType.ADDED, kind=Kind.POD, resource=pod1, version=1),
            K8SEvent(event=EventType.MODIFIED, kind=Kind.POD, resource=pod2, version=2),
            K8SEvent(event=EventType.MODIFIED, kind=Kind.POD, resource=pod3, version=3),
            K8SEvent(event=EventType.DELETED, kind=Kind.POD, resource=pod4, version=4),
        ]
        self.k8s_client.mock_watched_pods(events)

        self.tasks.append(self.loop.create_task(self.pool.subscribe()))

        result = self.wait_for_result(2, 1)

        self.assertEqual(result, [pod4])
        self.assertEqual(result[0]["status"]["phase"], "Succeeded")

    def wait_for_result(self, seconds: int, count: int) -> List[Dict[str, Any]]:
        start = datetime.datetime.now()
        result = []
        while start + datetime.timedelta(seconds=seconds) > datetime.datetime.now():
            terminated = self.pool.drain_terminated()
            result.extend(terminated)
            if len(result) >= count:
                return result
            self.loop.run_until_complete(asyncio.sleep(0.1))
        raise AssertionError("time is up.")
