from typing import Any, Dict, List, Set

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
        results: List[Dict[str, Any]] = []
        all_node_ids = graph.get_ids()
        aggregate_ids = set()
        for node_id in sorted(all_node_ids):
            meta_properties = graph.get_node_meta_properties(node_id)
            rdf_type = meta_properties.get("rdf:type")
            if rdf_type and rdf_type in self.config.aggregates:
                aggregate_ids.add(node_id)

        queue = sorted(list(aggregate_ids))
        self.write_nodes(results, graph, queue, all_node_ids, aggregate_ids)

        queue = sorted(list(set(all_node_ids) - aggregate_ids))
        self.write_nodes(results, graph, queue, all_node_ids, aggregate_ids)

        outcome: Dict[str, Any] = {}
        default_context = self.config.contexts.get("__default__")
        if default_context:
            outcome["@context"] = default_context
        outcome["@graph"] = results

        out.write(json.dumps(outcome))
        out.flush()

    def write_nodes(
        self,
        out_results: List[Dict[str, Any]],
        graph: Graph,
        queue: List[str],
        all_node_ids: Set[str],
        aggregate_ids: Set[str],
    ) -> None:
        while len(queue) > 0:
            node_id, queue = queue[0], queue[1:]
            if node_id in all_node_ids:
                result_node = self.write_node(
                    graph, node_id, all_node_ids, aggregate_ids
                )
                out_results.append(result_node)

    def write_node(
        self,
        graph: Graph,
        node_id: str,
        all_node_ids: Set[str],
        aggregate_ids: Set[str],
    ) -> Dict[str, Any]:
        all_node_ids.remove(node_id)
        result_node: Dict[str, Any] = {}
        result_node["@id"] = node_id

        meta_properties = dict(sorted(graph.get_node_meta_properties(node_id).items()))
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
                    value = next(iter(values))
                    if value not in aggregate_ids and value in all_node_ids:
                        result_node[predicate] = self.write_node(
                            graph, value, all_node_ids, aggregate_ids
                        )
                    else:
                        result_node[predicate] = value
                else:
                    relation_nodes = list()
                    for value_id in sorted(list(values)):
                        if value_id not in aggregate_ids and value_id in all_node_ids:
                            relation_nodes.append(
                                self.write_node(
                                    graph, value_id, all_node_ids, aggregate_ids
                                )
                            )
                        else:
                            relation_nodes.append(value_id)
                    result_node[predicate] = {"@set": relation_nodes}
            else:
                if values not in aggregate_ids and value in all_node_ids:
                    result_node[predicate] = self.write_node(
                        graph, values, all_node_ids, aggregate_ids
                    )
                else:
                    result_node[predicate] = values

        return result_node

    def resolve_context(self, meta_properties: Dict[str, str]) -> Dict[str, str]:
        rdf_type = meta_properties.get("rdf:type")
        if not rdf_type:
            return dict()
        return self.config.contexts.get(rdf_type, dict())
