from abc import abstractmethod
from io import IOBase, StringIO

from app.kg.graph import Graph


class GraphSerializer:
    @abstractmethod
    def write(self, out: IOBase, graph: Graph) -> None:
        pass

    def to_string(self, graph: Graph) -> str:
        buffer = StringIO()
        self.write(buffer, graph)
        return buffer.getvalue()
