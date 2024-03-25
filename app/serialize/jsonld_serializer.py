from typing import Any, Dict, List, Set

import json
from io import IOBase

from app.kg.graph import Graph
from app.kg.id_base import IdBase
from app.kg.iri import IRI
from app.serialize.graph_serializer import GraphSerializer
from app.serialize.jsonld_configuration import JsonLDConfiguration


class JsonLDSerialializer(GraphSerializer):
    config: JsonLDConfiguration

    def __init__(self, config: JsonLDConfiguration):
        self.config = config

    def write(self, out: IOBase, graph: Graph) -> None:
        results: List[Dict[str, Any]] = []
        all_node_ids: Set[IRI] = graph.get_ids()
        aggregate_ids: Set[IRI] = set()
        for node_id in sorted(list(all_node_ids)):
            meta_properties = graph.get_node_meta_properties(node_id)
            rdf_type = meta_properties.get(Graph.RDF_TYPE_IRI)
            if rdf_type and rdf_type in self.config.aggregates:
                aggregate_ids.add(node_id)

        queue = sorted(list(aggregate_ids))
        self.write_nodes(results, graph, queue, all_node_ids, aggregate_ids)

        queue = sorted(list(set(all_node_ids) - aggregate_ids))
        self.write_nodes(results, graph, queue, all_node_ids, aggregate_ids)

        outcome: Dict[str, Any] = {}
        default_context = self.config.contexts.get(
            JsonLDConfiguration.DEFAULT_CONTEXT_IRI
        )
        if default_context:
            outcome["@context"] = default_context
        outcome["@graph"] = results
        out.write(json.dumps(outcome))
        out.flush()

    def write_nodes(
        self,
        out_results: List[Dict[str, Any]],
        graph: Graph,
        queue: List[IRI],
        all_node_ids: Set[IRI],
        aggregate_ids: Set[IRI],
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
        node_id: IRI,
        all_node_ids: Set[IRI],
        aggregate_ids: Set[IRI],
    ) -> Dict[str, Any]:
        all_node_ids.remove(node_id)
        result_node: Dict[str, Any] = {}
        result_node["@id"] = node_id.render()

        meta_properties = dict(sorted(graph.get_node_meta_properties(node_id).items()))
        rdf_type = meta_properties.get(Graph.RDF_TYPE_IRI)
        if rdf_type is None:
            raise Exception(f"Node {node_id} is expected to have a rdf:type.")
        result_node["@type"] = rdf_type.render()
        context = self.resolve_context(meta_properties)
        del meta_properties[Graph.RDF_TYPE_IRI]
        if len(context) > 0:
            result_node = {**result_node, **{"@context": context}}

        for predicate, value in meta_properties.items():
            result_node[predicate.render()] = value.render()

        node_properties = dict(sorted(graph.get_node_properties(node_id).items()))
        for predicate, values in node_properties.items():
            if type(values) is set:
                result_node[predicate.render()] = {
                    "@set": list(sorted([v.render() for v in values]))
                }
            else:
                result_node[predicate.render()] = values.render()

        node_relations = dict(sorted(graph.get_node_relations(node_id).items()))
        for predicate, values in node_relations.items():
            if type(values) is set:
                if len(values) == 1:
                    relation_iri: IRI = next(iter(values))
                    if (
                        relation_iri not in aggregate_ids
                        and relation_iri in all_node_ids
                    ):
                        result_node[predicate.render()] = self.write_node(
                            graph, relation_iri, all_node_ids, aggregate_ids
                        )
                    else:
                        result_node[predicate.render()] = relation_iri.render()
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
                            relation_nodes.append(value_id.render())
                    result_node[predicate.render()] = {"@set": relation_nodes}
            else:
                if values not in aggregate_ids and value in all_node_ids:
                    result_node[predicate.render()] = self.write_node(
                        graph, values, all_node_ids, aggregate_ids
                    )
                else:
                    result_node[predicate.render()] = values.render()

        return result_node

    def resolve_context(self, meta_properties: Dict[IRI, IdBase]) -> Dict[str, Any]:
        rdf_type = meta_properties.get(Graph.RDF_TYPE_IRI)
        if not rdf_type:
            return dict()
        return self.config.contexts.get(rdf_type, dict())
