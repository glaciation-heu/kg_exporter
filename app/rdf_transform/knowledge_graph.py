from typing import Any, Dict, Set, TypeAlias

from abc import abstractmethod

PropertyValue: TypeAlias = str | int | bool | float
PropertySet: TypeAlias = Set[PropertyValue]
RelationSet: TypeAlias = Set[str]


class KnowledgeGraph:
    @abstractmethod
    def add_property(
        self, subject_id: str, predicate: str, value: str | int | float | bool
    ) -> None:
        pass

    @abstractmethod
    def add_property_collection(
        self, subject_id: str, predicate: str, value: Set[str | int | float | bool]
    ) -> None:
        pass

    @abstractmethod
    def add_meta_property(
        self, subject_id: str, predicate: str, object_id: str
    ) -> None:
        pass

    @abstractmethod
    def add_relation(self, subject_id: str, predicate: str, object_id: str) -> None:
        pass

    @abstractmethod
    def add_relation_collection(
        self, subject_id: str, predicate: str, object_ids: Set[str]
    ) -> None:
        pass

    @abstractmethod
    def get_ids(self) -> Set[str]:
        pass

    @abstractmethod
    def get_node_properties(self, node_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_node_meta_properties(self, node_id: str) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_node_relations(self, node_id: str) -> Dict[str, Set[str]]:
        pass
