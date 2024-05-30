from typing import Any, Dict, List

from kubernetes import config, dynamic
from kubernetes.client import api_client

from app.clients.k8s.k8s_client import K8SClient
from app.clients.k8s.k8s_settings import K8SSettings


class K8SClientImpl(K8SClient):
    client: dynamic.DynamicClient

    def __init__(self, settings: K8SSettings):
        configuration = (
            config.load_incluster_config()
            if settings.in_cluster
            else config.load_kube_config()
        )
        self.client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=configuration)
        )

    async def get_nodes(self) -> List[Dict[str, Any]]:
        return await self.get_resource("Node")

    async def get_pods(self) -> List[Dict[str, Any]]:
        return await self.get_resource("Pod")

    async def get_deployments(self) -> List[Dict[str, Any]]:
        return await self.get_resource("Deployment")

    async def get_replicasets(self) -> List[Dict[str, Any]]:
        return await self.get_resource("Replicaset")

    async def get_daemonsets(self) -> List[Dict[str, Any]]:
        return await self.get_resource("Daemonset")

    async def get_statefullsets(self) -> List[Dict[str, Any]]:
        return await self.get_resource("StatefulSet")

    async def get_jobs(self) -> List[Dict[str, Any]]:
        return await self.get_resource("Job")

    async def get_resource(self, kind: str) -> List[Dict[str, Any]]:
        api = self.client.resources.get(api_version="v1", kind=kind)
        return [item.to_dict() for item in api.get().items]
