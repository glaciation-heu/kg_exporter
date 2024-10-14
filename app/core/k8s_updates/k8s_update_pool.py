from typing import Any, Dict, List


class K8SUpdatePool:
    def __init__(self):
        pass

    async def subscribe(self) -> None:
        raise NotImplementedError

    def drain_terminated(self) -> List[Dict[str, Any]]:
        raise NotImplementedError
