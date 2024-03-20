from typing import Any, Dict, Set

from app.kg.graph import Graph


class GraphNode:
    id: str
    properties: Dict[str, str | int | float | bool | Set[str | int | float | bool]]
    meta_properties: Dict[str, str]

    def __init__(self, node_id: str):
        self.id = node_id
        self.properties = {}
        self.meta_properties = {}

    def add_property(self, predicate: str, value: str | int | float | bool) -> None:
        if predicate in self.properties:
            self.add_property_collection(predicate, {value})
        else:
            self.properties[predicate] = value

    def add_meta_property(self, predicate: str, value: str) -> None:
        self.meta_properties[predicate] = value

    def add_property_collection(
        self, predicate: str, values: Set[str | int | float | bool]
    ) -> None:
        if predicate in self.properties:
            existing_value = self.properties[predicate]
            if type(existing_value) is set:
                self.properties[predicate] = existing_value.union(values)
            else:
                values.add(existing_value)  # type: ignore
                self.properties[predicate] = values
        else:
            self.properties[predicate] = values

    def get_properties(self) -> Dict[str, Any]:
        return self.properties

    def get_meta_properties(self) -> Dict[str, str]:
        return self.meta_properties


class GraphEdge:
    subject_id: str
    predicate: str
    objects: Set[str]

    def __init__(self, subject_id: str, predicate: str):
        self.subject_id = subject_id
        self.predicate = predicate
        self.objects = set()

    def add_object_id(self, object_id: str) -> None:
        self.objects.add(object_id)

    def get_objects(self) -> Set[str]:
        return self.objects


class InMemoryGraph(Graph):
    nodes: Dict[str, GraphNode]
    edges: Dict[str, Dict[str, GraphEdge]]

    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def get_or_add_node(self, node_id: str) -> GraphNode:
        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(node_id)
        return self.nodes[node_id]

    def get_or_add_edge(self, subject_id: str, predicate: str) -> GraphEdge:
        self.get_or_add_node(subject_id)
        if subject_id not in self.edges:
            self.edges[subject_id] = {}
        node_edges = self.edges[subject_id]
        if predicate not in node_edges:
            node_edges[predicate] = GraphEdge(subject_id, predicate)
        return node_edges[predicate]

    def add_property(
        self, subject_id: str, predicate: str, value: str | int | float | bool
    ) -> None:
        self.get_or_add_node(subject_id).add_property(predicate, value)

    def add_property_collection(
        self, subject_id: str, predicate: str, value: Set[str | int | float | bool]
    ) -> None:
        self.get_or_add_node(subject_id).add_property_collection(predicate, value)

    def add_meta_property(
        self, subject_id: str, predicate: str, object_id: str
    ) -> None:
        self.get_or_add_node(subject_id).add_meta_property(predicate, object_id)

    def add_relation(self, subject_id: str, predicate: str, object_id: str) -> None:
        self.get_or_add_node(object_id)
        self.get_or_add_edge(subject_id, predicate).add_object_id(object_id)

    def add_relation_collection(
        self, subject_id: str, predicate: str, object_ids: Set[str]
    ) -> None:
        edge = self.get_or_add_edge(subject_id, predicate)
        for object_id in object_ids:
            self.get_or_add_node(object_id)
            edge.add_object_id(object_id)

    def get_ids(self) -> Set[str]:
        return set(self.nodes.keys())

    def get_node_properties(self, node_id: str) -> Dict[str, Any]:
        node = self.nodes.get(node_id)
        if node:
            return node.get_properties()
        else:
            return {}

    def get_node_meta_properties(self, node_id: str) -> Dict[str, str]:
        node = self.nodes.get(node_id)
        if node:
            return node.get_meta_properties()
        else:
            return {}

    def get_node_relations(self, node_id: str) -> Dict[str, Set[str]]:
        edge_nodes = self.edges.get(node_id)
        if edge_nodes:
            return {
                predicate: edge.get_objects()
                for (predicate, edge) in edge_nodes.items()
            }
        else:
            return {}
