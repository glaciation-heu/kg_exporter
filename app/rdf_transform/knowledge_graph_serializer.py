from abc import abstractmethod

from app.rdf_transform.knowledge_graph import KnowledgeGraph


class KnowledgeGraphSerializer:
    @abstractmethod
    def write(self, graph: KnowledgeGraph) -> str:
        pass
