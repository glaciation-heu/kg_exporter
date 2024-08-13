from typing import Any, Dict, TypeVar

import asyncio
from io import StringIO

from app.clients.metadata_service.metadata_service_client import MetadataServiceClient
from app.core.kg.kg_query import KGQuery
from app.core.kg.kg_snapshot import KGSnapshot
from app.core.kg.resource_status_query import ResourceStatusQuery, ResourceType
from app.core.types import KGSliceId
from app.kg.graph import Graph
from app.serialize.jsonld_configuration import JsonLDConfiguration
from app.serialize.jsonld_serializer import JsonLDSerialializer
from app.transform.k8s.upper_ontology_base import UpperOntologyBase

T = TypeVar("T")


class KGRepository:
    node_query: ResourceStatusQuery
    pod_query: ResourceStatusQuery
    container_query: ResourceStatusQuery

    metadata_client: MetadataServiceClient

    def __init__(self, metadata_client: MetadataServiceClient):
        self.metadata_client = metadata_client
        self.node_query = ResourceStatusQuery(ResourceType.NODE)
        self.pod_query = ResourceStatusQuery(ResourceType.POD)
        self.container_query = ResourceStatusQuery(ResourceType.CONTAINER)

    async def query_snapshot(self, slice_id: KGSliceId) -> KGSnapshot:
        (nodes, pods, containers) = await asyncio.gather(
            self.query(slice_id, self.node_query),
            self.query(slice_id, self.pod_query),
            self.query(slice_id, self.container_query),
        )
        return KGSnapshot(nodes, pods, containers)

    async def query(self, slice_id: KGSliceId, query: KGQuery[T]) -> T:
        host_and_port = slice_id.get_host_port()
        result = await self.metadata_client.query(host_and_port, query.get_query())
        return query.parse_results(result)

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
