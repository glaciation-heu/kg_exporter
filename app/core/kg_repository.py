from dataclasses import dataclass

from app.clients.metadata.metadata_service_client import MetadataServiceClient
from app.kg.graph import Graph
from app.kg.inmemory_graph import InMemoryGraph


@dataclass
class ExistingResources:
    pass


class KGRepository:
    metadata_client: MetadataServiceClient

    def __init__(self, metadata_client: MetadataServiceClient):
        self.metadata_client = metadata_client

    async def query(self, query: str) -> Graph:
        return InMemoryGraph()

    async def update(self, graph: Graph) -> None:
        pass
