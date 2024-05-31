from typing import Dict, List, Optional, TypeAlias

from app.clients.metadata_service.metadata_service_client import (
    MetadataServiceClient,
    Triple,
)

HostId: TypeAlias = str
SparQLQuery: TypeAlias = str
SerializedGraph: TypeAlias = str


class HostInteractions:
    query_to_response: Dict[SparQLQuery, List[Triple]]
    inserts: List[SerializedGraph]

    def __init__(self):
        self.query_to_response = dict()
        self.inserts = []

    def add_query(self, sparql: SparQLQuery, result: List[Triple]) -> None:
        self.query_to_response[sparql] = result

    def get_query_result(self, sparql: SparQLQuery) -> Optional[List[Triple]]:
        return self.query_to_response.get(sparql)

    def add_insert(self, result: SerializedGraph) -> None:
        self.inserts.append(result)

    def get_inserts(self) -> List[SerializedGraph]:
        return self.inserts


class MockMetadataServiceClient(MetadataServiceClient):
    hosts: Dict[HostId, HostInteractions]

    def __init__(self):
        self.hosts = dict()

    def mock_query(
        self, host: HostId, sparql: SparQLQuery, result: List[Triple]
    ) -> None:
        if host not in self.hosts:
            self.hosts[host] = HostInteractions()
        self.hosts[host].add_query(sparql, result)

    async def query(self, host_and_port: HostId, sparql: SparQLQuery) -> List[Triple]:
        host_queries = self.hosts.get(host_and_port)
        if host_queries:
            return host_queries.get_query_result(sparql) or []
        return []

    def get_inserts(self, host: HostId) -> List[SerializedGraph]:
        host_interactions = self.hosts.get(host)
        if host_interactions:
            return host_interactions.get_inserts()
        else:
            return []

    async def insert(self, host_and_port: HostId, message: SerializedGraph) -> None:
        if host_and_port not in self.hosts:
            self.hosts[host_and_port] = HostInteractions()
        self.hosts[host_and_port].add_insert(message)
