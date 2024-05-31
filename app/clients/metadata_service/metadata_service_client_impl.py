from typing import List

import httpx
from httpx import HTTPError

from app.clients.metadata_service.metadata_service_client import (
    MetadataServiceClient,
    Triple,
)
from app.clients.metadata_service.metadata_service_settings import (
    MetadataServiceSettings,
)


class ClientError(Exception):
    pass


class MetadataServiceClientImpl(MetadataServiceClient):
    settings: MetadataServiceSettings

    def __init__(self, settings: MetadataServiceSettings):
        self.settings = settings

    async def query(self, host_and_port: str, sparql: str) -> List[Triple]:
        url = f"http://{host_and_port}/api/v0/graph/search"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    content=sparql,
                    headers=[("Content-Type", "application/json")],
                )
                response.raise_for_status()
                # TODO parse response
                return []
            except HTTPError as e:
                raise ClientError(e.args[0]) from e

    async def insert(self, host_and_port: str, graph: str) -> None:
        url = f"http://{host_and_port}/api/v0/graph"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(
                    url,
                    content=graph,
                    headers=[("Content-Type", "application/json")],
                )
                response.raise_for_status()
            except HTTPError as e:
                raise ClientError(e.args[0]) from e
