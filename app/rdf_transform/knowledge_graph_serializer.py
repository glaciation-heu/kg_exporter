from abc import abstractmethod
from io import IOBase

from app.rdf_transform.knowledge_graph import KnowledgeGraph


class KnowledgeGraphSerializer:
    @abstractmethod
    def write(self, out: IOBase, graph: KnowledgeGraph) -> None:
        pass
