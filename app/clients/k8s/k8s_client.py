from typing import Any, Dict, List

from dataclasses import dataclass, field


@dataclass
class ResourceSnapshot:
    pods: List[Dict[str, Any]] = field(default_factory=list)
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    deployments: List[Dict[str, Any]] = field(default_factory=list)
    jobs: List[Dict[str, Any]] = field(default_factory=list)
    statefullsets: List[Dict[str, Any]] = field(default_factory=list)
    daemonsets: List[Dict[str, Any]] = field(default_factory=list)
    replicasets: List[Dict[str, Any]] = field(default_factory=list)


class K8SClient:
    async def fetch_snapshot(self) -> ResourceSnapshot:
        nodes = await self.get_nodes()
        pods = await self.get_pods()
        deployments = await self.get_deployments()
        jobs = await self.get_jobs()
        statefullsets = await self.get_statefullsets()
        daemonsets = await self.get_daemonsets()
        replicasets = await self.get_replicasets()
        return ResourceSnapshot(
            pods=pods,
            nodes=nodes,
            deployments=deployments,
            jobs=jobs,
            statefullsets=statefullsets,
            daemonsets=daemonsets,
            replicasets=replicasets,
        )

    async def get_nodes(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def get_pods(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def get_replicasets(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def get_deployments(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def get_daemonsets(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def get_statefullsets(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def get_jobs(self) -> List[Dict[str, Any]]:
        raise NotImplementedError
