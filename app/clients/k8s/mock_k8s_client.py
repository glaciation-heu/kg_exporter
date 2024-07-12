from typing import Any, Dict, List

from app.clients.k8s.k8s_client import K8SClient


class MockK8SClient(K8SClient):
    nodes: List[Dict[str, Any]]
    pods: List[Dict[str, Any]]
    replicasets: List[Dict[str, Any]]
    deployments: List[Dict[str, Any]]
    daemonsets: List[Dict[str, Any]]
    statefullsets: List[Dict[str, Any]]
    jobs: List[Dict[str, Any]]
    cluster: Dict[str, Any]
    api_versions: Dict[str, Any]

    def __init__(self):
        self.nodes = []
        self.pods = []
        self.replicasets = []
        self.deployments = []
        self.daemonsets = []
        self.statefullsets = []
        self.jobs = []
        self.cluster = {}
        self.api_versions = {}

    def mock_api_versions(self, api_versions: Dict[str, Any]) -> None:
        self.api_versions = api_versions

    async def get_api_versions(self) -> Dict[str, Any]:
        return self.api_versions

    def mock_cluster(self, cluster: Dict[str, Any]) -> None:
        self.cluster = cluster

    async def get_cluster_info(self) -> Dict[str, Any]:
        return self.cluster

    def mock_nodes(self, nodes: List[Dict[str, Any]]) -> None:
        self.nodes = nodes

    async def get_nodes(self) -> List[Dict[str, Any]]:
        return self.nodes

    def mock_pods(self, pods: List[Dict[str, Any]]) -> None:
        self.pods = pods

    async def get_pods(self) -> List[Dict[str, Any]]:
        return self.pods

    def mock_replicasets(self, replicasets: List[Dict[str, Any]]) -> None:
        self.replicasets = replicasets

    async def get_replicasets(self) -> List[Dict[str, Any]]:
        return self.replicasets

    def mock_deployments(self, deployments: List[Dict[str, Any]]) -> None:
        self.deployments = deployments

    async def get_deployments(self) -> List[Dict[str, Any]]:
        return self.deployments

    def mock_daemonsets(self, daemonsets: List[Dict[str, Any]]) -> None:
        self.daemonsets = daemonsets

    async def get_daemonsets(self) -> List[Dict[str, Any]]:
        return self.daemonsets

    def mock_statefullsets(self, statefullsets: List[Dict[str, Any]]) -> None:
        self.statefullsets = statefullsets

    async def get_statefullsets(self) -> List[Dict[str, Any]]:
        return self.statefullsets

    def mock_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        self.jobs = jobs

    async def get_jobs(self) -> List[Dict[str, Any]]:
        return self.jobs
