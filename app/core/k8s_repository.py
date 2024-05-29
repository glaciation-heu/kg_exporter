from typing import Any, Dict, List

from dataclasses import dataclass, field

from app.clients.k8s.k8s_client import K8SClient


@dataclass
class ResourceSnapshot:
    pods: List[Dict[str, Any]] = field(default_factory=list)
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    deployments: List[Dict[str, Any]] = field(default_factory=list)
    jobs: List[Dict[str, Any]] = field(default_factory=list)
    statefullsets: List[Dict[str, Any]] = field(default_factory=list)
    daemonsets: List[Dict[str, Any]] = field(default_factory=list)
    replicasets: List[Dict[str, Any]] = field(default_factory=list)


class K8SRepository:
    k8s_client: K8SClient

    def __init__(self, k8s_client: K8SClient):
        self.k8s_client = k8s_client

    async def fetch_snapshot(self) -> ResourceSnapshot:
        return ResourceSnapshot()
