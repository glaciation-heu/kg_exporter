from typing import Any, Dict

import json
from io import IOBase

from app.kg.graph import Graph
from app.serialize.graph_serializer import GraphSerializer


class JsonLDSerialializer(GraphSerializer):
    contexts: Dict[str, Dict[str, str]]

    def __init__(self, contexts: Dict[str, Dict[str, str]]):
        self.contexts = contexts

    def add_prefix(self, out: IOBase, name: str, uri: str) -> None:
        out.write(f"PREFIX {name} {uri}\n")

    def write(self, out: IOBase, graph: Graph) -> None:
        results = []
        for node_id in sorted(graph.get_ids()):
            result_node: Dict[str, Any] = {}
            result_node["@id"] = node_id

            meta_properties = dict(
                sorted(graph.get_node_meta_properties(node_id).items())
            )
            rdf_type = meta_properties.get("rdf:type")
            if rdf_type is None:
                raise Exception(f"Node {node_id} is expected to have a rdf:type.")
            del meta_properties["rdf:type"]
            result_node["@type"] = rdf_type
            context = self.resolve_context(meta_properties)
            if len(context) > 0:
                result_node = {**result_node, **{"@context": context}}

            for predicate, value in meta_properties.items():
                result_node[predicate] = value

            node_properties = dict(sorted(graph.get_node_properties(node_id).items()))
            for predicate, values in node_properties.items():
                if type(values) is set:
                    result_node[predicate] = {"@set": list(sorted(values))}
                else:
                    result_node[predicate] = values

            node_relations = dict(sorted(graph.get_node_relations(node_id).items()))
            for predicate, values in node_relations.items():
                if type(values) is set:
                    if len(values) == 1:
                        result_node[predicate] = next(iter(values))
                    else:
                        result_node[predicate] = {"@set": sorted(list(values))}
                else:
                    result_node[predicate] = values
            results.append(result_node)
        out.write(json.dumps(results))
        out.flush()

    def resolve_context(self, meta_properties: Dict[str, str]) -> Dict[str, str]:
        rdf_type = meta_properties.get("rdf:type")
        if not rdf_type:
            return dict()
        return self.contexts.get(rdf_type, dict())
