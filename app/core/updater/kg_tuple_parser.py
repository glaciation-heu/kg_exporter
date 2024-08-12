from typing import Dict, List

from app.core.updater.kg_result_parser import KGResultParser
from app.kg.graph import Graph
from app.kg.id_base import IdBase
from app.kg.inmemory_graph import InMemoryGraph


class KGTupleParser(KGResultParser):
    def parse(self, result: List[Dict[str, IdBase]]) -> Graph:
        return InMemoryGraph()
