from typing import List

from app.clients.metadata_service.metadata_service_client import Triple
from app.core.kg_result_parser import KGResultParser
from app.kg.graph import Graph
from app.kg.inmemory_graph import InMemoryGraph


class KGTupleParser(KGResultParser):
    def parse(self, result: List[Triple]) -> Graph:
        return InMemoryGraph()
