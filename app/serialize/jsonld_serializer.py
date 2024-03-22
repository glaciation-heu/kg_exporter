from typing import Any, Dict

import json
from io import IOBase

from app.kg.graph import Graph
from app.serialize.graph_serializer import GraphSerializer
from app.serialize.jsonld_configuration import JsonLDConfiguration


class JsonLDSerialializer(GraphSerializer):
    config: JsonLDConfiguration

    def __init__(self, config: JsonLDConfiguration):
        self.config = config

    def write(self, out: IOBase, graph: Graph) -> None:
        results = []
        node_ids = sorted(graph.get_ids())
        while len(node_ids) > 0:
            node_id, node_ids = node_ids[0], node_ids[1:]
            result_node: Dict[str, Any] = {}
            result_node["@id"] = node_id

            meta_properties = dict(
                sorted(graph.get_node_meta_properties(node_id).items())
            )
            rdf_type = meta_properties.get("rdf:type")
            if rdf_type is None:
                raise Exception(f"Node {node_id} is expected to have a rdf:type.")
            result_node["@type"] = rdf_type
            context = self.resolve_context(meta_properties)
            del meta_properties["rdf:type"]
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
        return self.config.contexts.get(rdf_type, dict())
