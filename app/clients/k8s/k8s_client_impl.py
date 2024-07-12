from typing import Any, Callable, Coroutine, Dict, List, Optional, TypeVar

from kubernetes_asyncio import config
from kubernetes_asyncio.client import ApiClient
from kubernetes_asyncio.client.api.core_api import CoreApi
from kubernetes_asyncio.client.configuration import Configuration
from kubernetes_asyncio.dynamic import DynamicClient

from app.clients.k8s.k8s_client import K8SClient
from app.clients.k8s.k8s_settings import K8SSettings

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
        self, func: Callable[[DynamicClient], Coroutine[Any, Any, T]]
    ) -> T:
        if not self.configuration:
            self.configuration = Configuration()
            if self.settings.in_cluster:
                config.load_incluster_config(client_configuration=self.configuration)
            else:
                await config.load_kube_config(client_configuration=self.configuration)

        async with ApiClient(configuration=self.configuration) as client_api:
            async with DynamicClient(client_api) as dynamic_api:
                return await func(dynamic_api)
