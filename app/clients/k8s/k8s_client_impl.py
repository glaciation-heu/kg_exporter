from typing import Any, Callable, Coroutine, Dict, List, Optional, TypeVar

from kubernetes_asyncio import config
from kubernetes_asyncio.client import ApiClient
from kubernetes_asyncio.client.api.core_api import CoreApi
from kubernetes_asyncio.client.configuration import Configuration
from kubernetes_asyncio.dynamic import DynamicClient
from kubernetes_asyncio.watch import Watch
from loguru import logger

from app.clients.k8s.k8s_client import K8SClient
from app.clients.k8s.k8s_event import EventType, K8SEvent, Kind
from app.clients.k8s.k8s_settings import K8SSettings
from app.core.async_queue import AsyncQueue

T = TypeVar("T")


class K8SClientImpl(K8SClient):
    settings: K8SSettings
    configuration: Optional[Configuration]

    def __init__(self, settings: K8SSettings):
        self.settings = settings
        self.configuration = None

    async def get_nodes(self) -> List[Dict[str, Any]]:
        return await self.get_resource("Node")

    async def get_pods(self) -> List[Dict[str, Any]]:
        return await self.get_resource("Pod")

    async def get_deployments(self) -> List[Dict[str, Any]]:
        return await self.get_resource("Deployment")

    async def get_replicasets(self) -> List[Dict[str, Any]]:
        return await self.get_resource("ReplicaSet")

    async def get_daemonsets(self) -> List[Dict[str, Any]]:
        return await self.get_resource("DaemonSet")

    async def get_statefullsets(self) -> List[Dict[str, Any]]:
        return await self.get_resource("StatefulSet")

    async def get_jobs(self) -> List[Dict[str, Any]]:
        return await self.get_resource("Job")

    async def get_cluster_info(self) -> Dict[str, Any]:
        async def get_cluster_info_internal(
            dyn_client: DynamicClient,
        ) -> Dict[str, Any]:
            configmap_api = await dyn_client.resources.get(
                api_version="v1", kind="ConfigMap"
            )
            results = await configmap_api.get(
                namespace="kube-system", name="kubeadm-config"
            )
            if results:
                return results.to_dict()  # type: ignore
            else:
                return {}

        return await self.execute(get_cluster_info_internal)

    async def get_api_versions(self) -> Dict[str, Any]:
        async def get_api_versions_internal(
            dyn_client: DynamicClient,
        ) -> Dict[str, Any]:
            versions = await CoreApi(dyn_client.client).get_api_versions()
            if versions:
                return versions.to_dict()  # type: ignore
            else:
                return {}

        return await self.execute(get_api_versions_internal)

    async def get_resource(self, kind: str) -> List[Dict[str, Any]]:
        async def get_resource_internal(client: DynamicClient) -> List[Dict[str, Any]]:
            api = await client.resources.get(api_version="v1", kind=kind)
            result = await api.get()
            return [item.to_dict() for item in result.items]

        return await self.execute(get_resource_internal)

    async def execute(
        self,
        func: Callable[[DynamicClient | ApiClient], Coroutine[Any, Any, T]],
        is_dynamic_client: bool = True,
    ) -> T:
        await self.init_configuration()

        async with ApiClient(configuration=self.configuration) as client_api:
            if is_dynamic_client:
                async with DynamicClient(client_api) as dynamic_api:
                    return await func(dynamic_api)
            else:
                return await func(client_api)

    async def init_configuration(self) -> None:
        if not self.configuration:
            self.configuration = Configuration()
            if self.settings.in_cluster:
                config.load_incluster_config(client_configuration=self.configuration)
            else:
                await config.load_kube_config(client_configuration=self.configuration)

    async def watch_pods(self, queue: AsyncQueue[K8SEvent]) -> None:
        async def watch_internal(dyn_client: DynamicClient) -> None:
            watcher = Watch()
            v1_pods = await dyn_client.resources.get(api_version="v1", kind="Pod")

            async for e in v1_pods.watch(watcher=watcher):
                try:
                    type = e["type"]
                    object = e["object"]
                    kind = object.kind
                    version = object["metadata"]["resourceVersion"]
                    event = K8SEvent(
                        event=EventType[type],
                        kind=Kind[kind.upper()],
                        resource=object.to_dict(),
                        version=version,
                    )
                    queue.put_nowait(event)
                except Exception as e:
                    logger.error("K8S pod watcher error {exception}", exception=str(e))

        await self.execute(watch_internal, is_dynamic_client=True)

    async def watch_nodes(self, queue: AsyncQueue[K8SEvent]) -> None:
        async def watch_internal(dyn_client: DynamicClient) -> None:
            watcher = Watch()
            v1_nodes = await dyn_client.resources.get(api_version="v1", kind="Node")

            async for e in v1_nodes.watch(watcher=watcher):
                try:
                    type = e["type"]
                    object = e["object"]
                    kind = object.kind
                    version = object["metadata"]["resourceVersion"]
                    event = K8SEvent(
                        event=EventType[type],
                        kind=Kind[kind.upper()],
                        resource=object.to_dict(),
                        version=version,
                    )
                    queue.put_nowait(event)
                except Exception as e:
                    logger.error("K8S node watcher error {exception}", exception=str(e))

        await self.execute(watch_internal, is_dynamic_client=True)
