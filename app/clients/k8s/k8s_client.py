from typing import Any, Dict, List, Optional, Set

import asyncio
from dataclasses import dataclass, field

from jsonpath_ng.ext import parse


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

    def get_resource_names(self) -> Set[str]:
        names: Set[str] = set()
        names = {*names, *{self.get_resource_name(resource) for resource in self.pods}}
        names = {*names, *{self.get_resource_name(resource) for resource in self.nodes}}
        names = {
            *names,
            *{self.get_resource_name(resource) for resource in self.deployments},
        }
        names = {*names, *{self.get_resource_name(resource) for resource in self.jobs}}
        names = {
            *names,
            *{self.get_resource_name(resource) for resource in self.statefullsets},
        }
        names = {
            *names,
            *{self.get_resource_name(resource) for resource in self.daemonsets},
        }
        names = {
            *names,
            *{self.get_resource_name(resource) for resource in self.replicasets},
        }
        return names

    def find_resources_by_kind_and_identity(
        self, kind: str, identity: str
    ) -> List[Dict[str, Any]]:
        resources = self.get_resources_by_kind(kind)
        if resources:
            return [
                resource
                for resource in resources
                if self.get_resource_name(resource) == identity
            ]
        else:
            return []

    def get_resource_name(self, node: Dict[str, Any]) -> str:
        for match in parse("$.metadata.name").find(node):
            return str(match.value)
        raise Exception("Metadata does not contain name.")

    def get_resources_by_kind(self, kind: str) -> Optional[List[Dict[str, Any]]]:
        if kind == "Pod":
            return self.pods
        elif kind == "Node":
            return self.nodes
        elif kind == "Deployment":
            return self.deployments
        elif kind == "Job":
            return self.jobs
        elif kind == "StatefulSet":
            return self.statefullsets
        elif kind == "DaemonSet":
            return self.daemonsets
        elif kind == "ReplicaSet":
            return self.replicasets
        return None

    def add_resources_by_kind(self, kind: str, resources: List[Dict[str, Any]]) -> None:
        if kind == "Pod":
            self.pods.extend(resources)
        elif kind == "Node":
            self.nodes.extend(resources)
        elif kind == "Deployment":
            self.deployments.extend(resources)
        elif kind == "Job":
            self.jobs.extend(resources)
        elif kind == "StatefulSet":
            self.statefullsets.extend(resources)
        elif kind == "DaemonSet":
            self.daemonsets.extend(resources)
        elif kind == "ReplicaSet":
            self.replicasets.extend(resources)


class K8SClient:
    async def fetch_snapshot(self) -> ResourceSnapshot:
        resources = await asyncio.gather(
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
        ) = resources
        cluster_info = await self.get_cluster_info()
        return ResourceSnapshot(
            cluster=cluster_info,
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

    async def get_cluster_info(self) -> Dict[str, Any]:
        raise NotImplementedError