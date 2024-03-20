from abc import abstractmethod
from io import IOBase

from app.kg.graph import Graph


class GraphSerializer:
    @abstractmethod
    def write(self, out: IOBase, graph: Graph) -> None:
        pass
