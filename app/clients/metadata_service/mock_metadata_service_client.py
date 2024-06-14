from typing import Dict, List, Optional, Tuple, TypeAlias

import asyncio
import datetime

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

    def take_inserts(self) -> List[SerializedGraph]:
        inserts = self.inserts
        self.inserts = []
        return inserts


class MockMetadataServiceClient(MetadataServiceClient):
    hosts: Dict[HostId, HostInteractions]

    def __init__(self):
        self.hosts = dict()

    def mock_query(
        self, host_id: HostId, sparql: SparQLQuery, result: List[Triple]
    ) -> None:
        if host_id not in self.hosts:
            self.hosts[host_id] = HostInteractions()
        self.hosts[host_id].add_query(sparql, result)

    async def query(self, host_and_port: HostId, sparql: SparQLQuery) -> List[Triple]:
        host_queries = self.hosts.get(host_and_port)
        if host_queries:
            return host_queries.get_query_result(sparql) or []
        return []

    def take_inserts(self, host_id: HostId) -> List[SerializedGraph]:
        host_interactions = self.hosts.get(host_id)
        if host_interactions:
            return host_interactions.take_inserts()
        else:
            return []

    def take_all_inserts(self) -> List[Tuple[HostId, SerializedGraph]]:
        result = []
        for host_id, host_interaction in self.hosts.items():
            inserts = [(host_id, insert) for insert in host_interaction.take_inserts()]
            result.extend(inserts)
        return result

    async def insert(self, host_and_port: HostId, message: SerializedGraph) -> None:
        if host_and_port not in self.hosts:
            self.hosts[host_and_port] = HostInteractions()
        self.hosts[host_and_port].add_insert(message)

    def wait_for_inserts(
        self, seconds: int, count: int
    ) -> List[Tuple[HostId, SerializedGraph]]:
        start = datetime.datetime.now()
        result = []
        while start + datetime.timedelta(seconds=seconds) > datetime.datetime.now():
            graphs = self.take_all_inserts()
            print(len(graphs))
            result.extend(graphs)
            if len(graphs) == count:
                return graphs
            asyncio.run(asyncio.sleep(0.5))
        raise AssertionError("time is up.")

    def wait_for_inserts2(
        self, runner: asyncio.Runner, seconds: int, count: int
    ) -> List[Tuple[HostId, SerializedGraph]]:
        start = datetime.datetime.now()
        result = []
        while start + datetime.timedelta(seconds=seconds) > datetime.datetime.now():
            graphs = self.take_all_inserts()
            result.extend(graphs)
            if len(graphs) == count:
                return graphs
            runner.run(asyncio.sleep(0.5))
        raise AssertionError("time is up.")
