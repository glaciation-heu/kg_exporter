from typing import Any, Dict, List, override

from app.clients.k8s.k8s_client import K8SClient


class MockK8SClient(K8SClient):
    nodes: List[Dict[str, Any]]
    pods: List[Dict[str, Any]]
    replicasets: List[Dict[str, Any]]
    deployments: List[Dict[str, Any]]
    daemonsets: List[Dict[str, Any]]
    statefullsets: List[Dict[str, Any]]
    jobs: List[Dict[str, Any]]

    def __init__(self):
        self.nodes = []
        self.pods = []
        self.replicasets = []
        self.deployments = []
        self.daemonsets = []
        self.statefullsets = []
        self.jobs = []

    def mock_nodes(self, nodes: List[Dict[str, Any]]) -> None:
        self.nodes = nodes

    @override
    async def get_nodes(self) -> List[Dict[str, Any]]:
        return self.nodes

    def mock_pods(self, pods: List[Dict[str, Any]]) -> None:
        self.pods = pods

    @override
    async def get_pods(self) -> List[Dict[str, Any]]:
        return self.pods

    def mock_replicasets(self, replicasets: List[Dict[str, Any]]) -> None:
        self.replicasets = replicasets

    @override
    async def get_replicasets(self) -> List[Dict[str, Any]]:
        return self.replicasets

    def mock_deployments(self, deployments: List[Dict[str, Any]]) -> None:
        self.deployments = deployments

    @override
    async def get_deployments(self) -> List[Dict[str, Any]]:
        return self.deployments

    def mock_daemonsets(self, daemonsets: List[Dict[str, Any]]) -> None:
        self.daemonsets = daemonsets

    @override
    async def get_daemonsets(self) -> List[Dict[str, Any]]:
        return self.daemonsets

    def mock_statefullsets(self, statefullsets: List[Dict[str, Any]]) -> None:
        self.statefullsets = statefullsets

    @override
    async def get_statefullsets(self) -> List[Dict[str, Any]]:
        return self.statefullsets

    def mock_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        self.jobs = jobs

    @override
    async def get_jobs(self) -> List[Dict[str, Any]]:
        return self.jobs
