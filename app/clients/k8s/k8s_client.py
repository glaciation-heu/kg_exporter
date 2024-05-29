from typing import Any, Dict, List


class K8SClient:
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
