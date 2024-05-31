from io import StringIO

from app.clients.metadata_service.metadata_service_client import MetadataServiceClient
from app.core.kg_result_parser import KGResultParser
from app.core.types import KGSliceId
from app.kg.graph import Graph
from app.serialize.jsonld_configuration import JsonLDConfiguration
from app.serialize.jsonld_serializer import JsonLDSerialializer


class KGRepository:
    metadata_client: MetadataServiceClient
    jsonld_config: JsonLDConfiguration

    def __init__(
        self, metadata_client: MetadataServiceClient, jsonld_config: JsonLDConfiguration
    ):
        self.metadata_client = metadata_client
        self.jsonld_config = jsonld_config

    async def query(
        self, slice_id: KGSliceId, query: str, result_parser: KGResultParser
    ) -> Graph:
        host_and_port = slice_id.get_host_port()
        result = await self.metadata_client.query(host_and_port, query)
        return result_parser.parse(result)

    async def update(self, slice_id: KGSliceId, graph: Graph) -> None:
        graph_str = self.to_jsonld(graph)
        host_and_port = slice_id.get_host_port()
        await self.metadata_client.insert(host_and_port, graph_str)

    def to_jsonld(self, graph: Graph) -> str:
        serializer = JsonLDSerialializer(self.jsonld_config)
        out = StringIO()
        serializer.write(out, graph)
        return out.getvalue()
