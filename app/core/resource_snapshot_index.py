from typing import Any, Dict, List, Optional, Tuple, TypeAlias

from app.clients.k8s.k8s_client import ResourceSnapshot

Kind: TypeAlias = str
Name: TypeAlias = str


class ResourceSnapshotIndex:
    index: Dict[Tuple[Kind, Name], Dict[str, Any]]

    def __init__(self):
        self.index = dict()

    @staticmethod
    def build(snapshot: ResourceSnapshot) -> "ResourceSnapshotIndex":
        index = ResourceSnapshotIndex()
        index.add("Node", snapshot.nodes)
        index.add("Pod", snapshot.pods)
        index.add("Deployment", snapshot.deployments)
        index.add("ReplicaSet", snapshot.replicasets)
        index.add("DaemonSet", snapshot.daemonsets)
        index.add("StatefulSet", snapshot.statefullsets)
        index.add("Job", snapshot.jobs)
        return index

    def add(self, kind: str, resources: List[Dict[str, Any]]) -> None:
        for resource in resources:
            name = resource["metadata"]["name"]
            self.index[(kind, name)] = resource

    def get_by(self, kind: str, name: str) -> Optional[Dict[str, Any]]:
        return self.index.get((kind, name))
