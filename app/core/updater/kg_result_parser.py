from typing import Dict, List

from app.kg.graph import Graph
from app.kg.id_base import IdBase


class KGResultParser:
    def parse(self, result: List[Dict[str, IdBase]]) -> Graph:
        raise NotImplementedError
