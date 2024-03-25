from typing import Any, Dict, Set

from abc import abstractmethod

from app.kg.id_base import IdBase
from app.kg.iri import IRI
from app.kg.literal import Literal
from app.kg.types import LiteralSet, RelationSet


class Graph:
    RDF_TYPE_IRI = IRI("rdf", "type")
    RDF_SUBCLASSOF_IRI = IRI("rdf", "subClassOf")

    @abstractmethod
    def add_property(self, subject_id: IRI, predicate: IRI, value: Literal) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_property_collection(
        self, subject_id: IRI, predicate: IRI, value: LiteralSet
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_meta_property(
        self, subject_id: IRI, predicate: IRI, object_id: IdBase
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_relation(self, subject_id: IRI, predicate: IRI, object_id: IRI) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_relation_collection(
        self, subject_id: IRI, predicate: IRI, object_ids: RelationSet
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_ids(self) -> Set[IRI]:
        raise NotImplementedError

    @abstractmethod
    def get_node_properties(self, node_id: IRI) -> Dict[IRI, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_node_meta_properties(self, node_id: IRI) -> Dict[IRI, IdBase]:
        raise NotImplementedError

    @abstractmethod
    def get_node_relations(self, node_id: IRI) -> Dict[IRI, RelationSet]:
        raise NotImplementedError
