from typing import Any, Dict, List, Set

import json
from io import IOBase

from app.kg.graph import Graph
from app.kg.id_base import IdBase
from app.kg.iri import IRI
from app.kg.literal import Literal, PropertyValue
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
        default_context = self.config.contexts.get(
            JsonLDConfiguration.DEFAULT_CONTEXT_IRI, dict()
        )
        for node_id in sorted(list(all_node_ids)):
            meta_properties = graph.get_node_meta_properties(node_id)
            rdf_type = meta_properties.get(Graph.RDF_TYPE_IRI)
            if rdf_type and rdf_type in self.config.aggregates:
                aggregate_ids.add(node_id)

        queue = sorted(list(aggregate_ids))
        self.write_nodes(
            results, graph, queue, all_node_ids, aggregate_ids, default_context
        )

        queue = sorted(list(set(all_node_ids) - aggregate_ids))
        self.write_nodes(
            results, graph, queue, all_node_ids, aggregate_ids, default_context
        )

        outcome: Dict[str, Any] = {}
        if len(default_context) > 0:
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
        default_context: Dict[str, Any],
    ) -> None:
        for node_id in queue:
            if node_id in all_node_ids:
                result_node = self.write_node(
                    graph, node_id, all_node_ids, aggregate_ids, default_context
                )
                out_results.append(result_node)

    def write_node(
        self,
        graph: Graph,
        node_id: IRI,
        all_node_ids: Set[IRI],
        aggregate_ids: Set[IRI],
        default_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        all_node_ids.remove(node_id)
        result_node: Dict[str, Any] = {}
        result_node["@id"] = node_id.render()

        meta_properties = dict(sorted(graph.get_node_meta_properties(node_id).items()))
        rdf_type = meta_properties.get(Graph.RDF_TYPE_IRI)
        if not rdf_type:
            raise Exception(
                f"Node {node_id} is expected to have a 'rdf:type' property."
            )
        result_node["@type"] = rdf_type.render()

        local_context = self.resolve_context(meta_properties)

        del meta_properties[Graph.RDF_TYPE_IRI]
        if len(local_context) > 0:
            result_node = {**result_node, **{"@context": local_context}}

        self.validate_prefix(rdf_type, default_context, local_context)
        self.validate_prefix(node_id, default_context, local_context)

        for predicate, value in meta_properties.items():
            self.validate_prefix(predicate, default_context, local_context)
            self.validate_prefix(value, default_context, local_context)
            result_node[predicate.render()] = self.get_value(value)

        node_properties = dict(sorted(graph.get_node_properties(node_id).items()))
        for predicate, values in node_properties.items():
            self.validate_prefix(predicate, default_context, local_context)
            if isinstance(values, set):
                result_node[predicate.render()] = {
                    "@set": list(sorted([self.get_value(v) for v in values]))
                }
            else:
                result_node[predicate.render()] = self.get_value(values)

        node_relations = dict(sorted(graph.get_node_relations(node_id).items()))
        for predicate, relation_object in node_relations.items():
            self.validate_prefix(predicate, default_context, local_context)
            if len(relation_object) == 1:
                relation_iri: IRI = next(iter(relation_object))
                if relation_iri not in aggregate_ids and relation_iri in all_node_ids:
                    result_node[predicate.render()] = self.write_node(
                        graph,
                        relation_iri,
                        all_node_ids,
                        aggregate_ids,
                        default_context,
                    )
                else:
                    self.validate_prefix(relation_iri, default_context, local_context)
                    result_node[predicate.render()] = relation_iri.render()
            else:
                relation_nodes: List[Any] = list()
                for value_id in sorted(list(relation_object)):
                    if value_id not in aggregate_ids and value_id in all_node_ids:
                        relation_nodes.append(
                            self.write_node(
                                graph,
                                value_id,
                                all_node_ids,
                                aggregate_ids,
                                default_context,
                            )
                        )
                    else:
                        self.validate_prefix(value_id, default_context, local_context)
                        relation_nodes.append(value_id.render())
                result_node[predicate.render()] = {"@set": relation_nodes}

        return result_node

    def resolve_context(self, meta_properties: Dict[IRI, IdBase]) -> Dict[str, Any]:
        rdf_type = meta_properties.get(Graph.RDF_TYPE_IRI)
        if not rdf_type:
            return dict()
        return self.config.contexts.get(rdf_type, dict())

    def get_value(self, base: IdBase) -> PropertyValue:
        if isinstance(base, Literal):
            return base.value
        elif isinstance(base, IRI):
            return base.render()
        else:
            raise Exception(f"Unexpected type {type(base)}, must one of (Literal, IRI)")

    def validate_prefix(
        self,
        iri: IdBase,
        default_context: Dict[str, Any],
        local_context: Dict[str, Any],
    ) -> None:
        prefix = iri.get_prefix()
        if prefix:
            if prefix in default_context:
                return
            elif prefix in local_context:
                return
            else:
                raise Exception(
                    f"Prefix for {iri.render()} cannot be found in any context."
                )
