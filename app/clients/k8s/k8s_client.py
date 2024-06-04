from typing import Any, Dict, List

import asyncio
from dataclasses import dataclass, field


@dataclass
class ResourceSnapshot:
    cluster: Dict[str, Any] = field(default_factory=dict)
    pods: List[Dict[str, Any]] = field(default_factory=list)
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    deployments: List[Dict[str, Any]] = field(default_factory=list)
    jobs: List[Dict[str, Any]] = field(default_factory=list)
    statefullsets: List[Dict[str, Any]] = field(default_factory=list)
    daemonsets: List[Dict[str, Any]] = field(default_factory=list)
    replicasets: List[Dict[str, Any]] = field(default_factory=list)


class K8SClient:
    async def fetch_snapshot(self) -> ResourceSnapshot:
        result = await asyncio.gather(
            self.get_nodes(),
            self.get_pods(),
            self.get_deployments(),
            self.get_jobs(),
            self.get_statefullsets(),
            self.get_daemonsets(),
            self.get_replicasets(),
        )
        (
            nodes,
            pods,
            deployments,
            jobs,
            statefullsets,
            daemonsets,
            replicasets,
        ) = result
        return ResourceSnapshot(
            cluster=dict(),
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
