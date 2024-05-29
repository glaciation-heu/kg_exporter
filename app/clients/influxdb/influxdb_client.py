from typing import Any, List


class InfluxDBClient:
    async def query(self, query: str) -> List[Any]:
        raise NotImplementedError
