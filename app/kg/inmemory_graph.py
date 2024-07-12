from typing import Any, Dict, Set

from app.kg.graph import Graph
from app.kg.id_base import IdBase
from app.kg.iri import IRI
from app.kg.literal import Literal
from app.kg.types import LiteralSet, RelationSet


class GraphNode:
    id: IRI
    properties: Dict[IRI, Literal | LiteralSet]
    meta_properties: Dict[IRI, IdBase]

    def __init__(self, node_id: IRI):
        self.id = node_id
        self.properties = dict()
        self.meta_properties = dict()

    def add_property(self, predicate: IRI, value: Literal) -> None:
        if predicate in self.properties:
            if self.properties[predicate] != value:
                self.add_property_collection(predicate, {value})
        else:
            self.properties[predicate] = value

    def add_meta_property(self, predicate: IRI, value: IdBase) -> None:
        self.meta_properties[predicate] = value

    def add_property_collection(self, predicate: IRI, values: LiteralSet) -> None:
        if predicate in self.properties:
            existing_value = self.properties[predicate]
            if type(existing_value) is set:
                self.properties[predicate] = existing_value.union(values)
            else:
                values.add(existing_value)  # type: ignore
                self.properties[predicate] = values
        else:
            self.properties[predicate] = values

    def get_properties(self) -> Dict[IRI, Any]:
        return self.properties

    def get_meta_properties(self) -> Dict[IRI, IdBase]:
        return self.meta_properties

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, GraphNode):
            return (
                self.id == other.id
                and self.properties == other.properties
                and self.meta_properties == other.meta_properties
            )
        else:
            raise NotImplementedError


class GraphEdge:
    subject_id: IRI
    predicate: IRI
    objects: Set[IRI]

    def __init__(self, subject_id: IRI, predicate: IRI):
        self.subject_id = subject_id
        self.predicate = predicate
        self.objects = set()

    def add_object_id(self, object_id: IRI) -> None:
        self.objects.add(object_id)

    def get_objects(self) -> Set[IRI]:
        return self.objects

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, GraphEdge):
            return (
                self.subject_id == other.subject_id
                and self.predicate == other.predicate
                and self.objects == other.objects
            )
        else:
            raise NotImplementedError


class InMemoryGraph(Graph):
    nodes: Dict[IRI, GraphNode]
    edges: Dict[IRI, Dict[IRI, GraphEdge]]

    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def get_or_add_node(self, node_id: IRI) -> GraphNode:
        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(node_id)
        return self.nodes[node_id]

    def get_or_add_edge(self, subject_id: IRI, predicate: IRI) -> GraphEdge:
        self.get_or_add_node(subject_id)
        if subject_id not in self.edges:
            self.edges[subject_id] = {}
        node_edges = self.edges[subject_id]
        if predicate not in node_edges:
            node_edges[predicate] = GraphEdge(subject_id, predicate)
        return node_edges[predicate]

    def add_property(self, subject_id: IRI, predicate: IRI, value: Literal) -> None:
        self.get_or_add_node(subject_id).add_property(predicate, value)

    def add_property_collection(
        self, subject_id: IRI, predicate: IRI, value: LiteralSet
    ) -> None:
        self.get_or_add_node(subject_id).add_property_collection(predicate, value)

    def add_meta_property(
        self, subject_id: IRI, predicate: IRI, object_id: IdBase
    ) -> None:
        self.get_or_add_node(subject_id).add_meta_property(predicate, object_id)

    def add_relation(self, subject_id: IRI, predicate: IRI, object_id: IRI) -> None:
        self.get_or_add_node(object_id)
        self.get_or_add_edge(subject_id, predicate).add_object_id(object_id)

    def add_relation_collection(
        self, subject_id: IRI, predicate: IRI, object_ids: RelationSet
    ) -> None:
        edge = self.get_or_add_edge(subject_id, predicate)
        for object_id in object_ids:
            self.get_or_add_node(object_id)
            edge.add_object_id(object_id)

    def has_node(self, node_id: IRI) -> bool:
        return node_id in self.nodes

    def get_ids(self) -> Set[IRI]:
        return set(self.nodes.keys())

    def get_node_properties(self, node_id: IRI) -> Dict[IRI, Any]:
        node = self.nodes.get(node_id)
        if node:
            return node.get_properties()
        else:
            return {}

    def get_node_meta_properties(self, node_id: IRI) -> Dict[IRI, IdBase]:
        node = self.nodes.get(node_id)
        if node:
            return node.get_meta_properties()
        else:
            return {}

    def get_node_relations(self, node_id: IRI) -> Dict[IRI, RelationSet]:
        edge_nodes = self.edges.get(node_id)
        if edge_nodes:
            return {
                predicate: edge.get_objects()
                for (predicate, edge) in edge_nodes.items()
            }
        else:
            return {}

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, InMemoryGraph):
            return self.nodes == other.nodes and self.edges == other.edges
        else:
            raise NotImplementedError
