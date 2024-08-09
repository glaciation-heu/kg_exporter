from typing import Dict, List

from app.kg.id_base import IdBase


class MetadataServiceClient:
    async def query(self, host_and_port: str, sparql: str) -> List[Dict[str, IdBase]]:
        raise NotImplementedError

    async def insert(self, host_and_port: str, message: str) -> None:
        raise NotImplementedError
