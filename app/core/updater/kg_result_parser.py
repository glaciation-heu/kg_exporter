from typing import List

from app.clients.metadata_service.metadata_service_client import Triple
from app.kg.graph import Graph


class KGResultParser:
    def parse(self, result: List[Triple]) -> Graph:
        raise NotImplementedError
