from typing import Any, Dict, List

from app.core.k8s_updates.k8s_update_pool import K8SUpdatePool


class MockK8SUpdatePool(K8SUpdatePool):
    def __init__(self):
        pass

    async def subscribe(self) -> None:
        pass

    def drain_terminated(self) -> List[Dict[str, Any]]:
        return []
