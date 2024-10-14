from typing import Any, Dict, List

import asyncio

from app.clients.k8s.k8s_client import K8SClient
from app.clients.k8s.k8s_event import EventType, K8SEvent, Kind
from app.core.async_queue import AsyncQueue
from app.core.k8s_updates.k8s_update_pool import K8SUpdatePool


class K8SUpdatePoolImpl(K8SUpdatePool):
    k8s_client: K8SClient
    last_pod_event: Dict[str, K8SEvent]
    last_node_event: Dict[str, K8SEvent]
    queue: AsyncQueue[K8SEvent]

    def __init__(self, k8s_client: K8SClient):
        self.k8s_client = k8s_client
        self.last_pod_event = dict()
        self.last_node_event = dict()
        self.queue = AsyncQueue[K8SEvent]()

    async def subscribe(self) -> None:
        await asyncio.gather(
            self.k8s_client.watch_pods(self.queue),
            self.k8s_client.watch_nodes(self.queue),
        )

    def drain_terminated(self) -> List[Dict[str, Any]]:
        self.receive_from_queue()
        return self.drain_deleted_pods()

    def drain_deleted_pods(self) -> List[Dict[str, Any]]:
        results = []
        to_delete = []
        for pod_id, last_event in self.last_pod_event.items():
            if last_event.event == EventType.DELETED:
                pod = last_event.resource
                if pod["status"]["phase"] == "Running":
                    pod["status"]["phase"] = "Succeeded"
                results.append(pod)
                to_delete.append(pod_id)
        for pod_id in to_delete:
            del self.last_pod_event[pod_id]
        return results

    def receive_from_queue(self) -> None:
        while True:
            event = self.queue.get_nowait()
            if not event:
                break
            if event.kind == Kind.POD:
                resource = event.resource
                name = resource["metadata"]["name"]
                namespace = resource["metadata"]["namespace"]
                identity = f"{namespace}.{name}"

                last_event = self.last_pod_event.get(identity)
                if not last_event or last_event.version < event.version:
                    self.last_pod_event[identity] = event

            elif event.kind == Kind.NODE:
                resource = event.resource
                identity = resource["metadata"]["name"]

                last_event = self.last_node_event.get(identity)
                if not last_event or last_event.version < event.version:
                    self.last_node_event[identity] = event
