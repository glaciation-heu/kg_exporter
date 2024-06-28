from typing import Any, Dict

from io import StringIO

from app.clients.metadata_service.metadata_service_client import MetadataServiceClient
from app.core.types import KGSliceId
from app.core.updater.kg_result_parser import KGResultParser
from app.kg.graph import Graph
from app.serialize.jsonld_configuration import JsonLDConfiguration
from app.serialize.jsonld_serializer import JsonLDSerialializer
from app.transform.k8s.upper_ontology_base import UpperOntologyBase


class KGRepository:
    metadata_client: MetadataServiceClient

    def __init__(self, metadata_client: MetadataServiceClient):
        self.metadata_client = metadata_client

    async def query(
        self, slice_id: KGSliceId, query: str, result_parser: KGResultParser
    ) -> Graph:
        host_and_port = slice_id.get_host_port()
        result = await self.metadata_client.query(host_and_port, query)
        return result_parser.parse(result)

    async def update(
        self, slice_id: KGSliceId, graph: Graph, context: Dict[str, Any]
    ) -> None:
        graph_str = self.to_jsonld(graph, context)
        host_and_port = slice_id.get_host_port()
        await self.metadata_client.insert(host_and_port, graph_str)

    def to_jsonld(self, graph: Graph, context: Dict[str, Any]) -> str:
        serializer = JsonLDSerialializer(self.get_jsonld_config(context))
        out = StringIO()
        serializer.write(out, graph)
        return out.getvalue()

    def get_jsonld_config(self, context: Dict[str, Any]) -> JsonLDConfiguration:
        return JsonLDConfiguration(
            {JsonLDConfiguration.DEFAULT_CONTEXT_IRI: context},
            {
                UpperOntologyBase.WORK_PRODUCING_RESOURCE,
                UpperOntologyBase.ASPECT,
                UpperOntologyBase.MEASUREMENT_PROPERTY,
                UpperOntologyBase.MEASURING_RESOURCE,
                UpperOntologyBase.MEASUREMENT_UNIT,
            },
        )
