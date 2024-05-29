from typing import List

from app.clients.metadata.model import Triple


class MetadataServiceClient:
    async def query(self, host_and_port: str, sparql: str) -> List[Triple]:
        raise NotImplementedError

    async def insert(self, host_and_port: str, graph: str) -> None:
        raise NotImplementedError
