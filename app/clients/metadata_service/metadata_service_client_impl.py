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
        base_url = self.get_base_url(host_and_port)
        url = f"{base_url}/api/v0/graph/search"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    content=sparql,
                    headers=[("Content-Type", "application/json")],
                )
                response.raise_for_status()
                # TODO parse response when it is clear what Metadata Service query API is
                return []
            except HTTPError as e:
                raise ClientError(e.args[0]) from e

    async def insert(self, host_and_port: str, graph: str) -> None:
        base_url = self.get_base_url(host_and_port)
        url = f"{base_url}/api/v0/graph"
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

    def get_base_url(self, host_and_port: str) -> str:
        if self.settings.use_single_url:
            return f"http://{self.settings.metadata_service_url}"
        else:
            return f"http://{host_and_port}"
