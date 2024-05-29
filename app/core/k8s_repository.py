from typing import List

from dataclasses import dataclass, field

from app.clients.k8s.k8s_client import K8SClient


@dataclass
class ClusterSnapshot:
    pods: List[str] = field(default_factory=list)
    nodes: List[str] = field(default_factory=list)
    deployments: List[str] = field(default_factory=list)
    jobs: List[str] = field(default_factory=list)
    statefullsets: List[str] = field(default_factory=list)
    daemonsets: List[str] = field(default_factory=list)
    replicasets: List[str] = field(default_factory=list)


class K8SRepository:
    k8s_client: K8SClient

    def __init__(self, k8s_client: K8SClient):
        self.k8s_client = k8s_client

    async def fetch_snapshot(self) -> ClusterSnapshot:
        return ClusterSnapshot()
