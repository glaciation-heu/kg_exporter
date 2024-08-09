from typing import Dict, List

import httpx
from httpx import HTTPError

from app.clients.metadata_service.metadata_service_client import MetadataServiceClient
from app.clients.metadata_service.metadata_service_settings import (
    MetadataServiceSettings,
)
from app.clients.metadata_service.query_response_parser import QueryResponseParser
from app.kg.id_base import IdBase


class ClientError(Exception):
    pass


class MetadataServiceClientImpl(MetadataServiceClient):
    settings: MetadataServiceSettings
    query_reponse_parser: QueryResponseParser

    def __init__(self, settings: MetadataServiceSettings):
        self.settings = settings
        self.query_reponse_parser = QueryResponseParser()

    async def query(self, host_and_port: str, sparql: str) -> List[Dict[str, IdBase]]:
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
                return self.query_reponse_parser.parse(response.text)
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
