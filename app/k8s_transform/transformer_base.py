from typing import Any, Dict, Optional, Set, Tuple

import re

from jsonpath_ng.ext import parse

from app.k8s_transform.transformation_context import TransformationContext
from app.k8s_transform.upper_ontology_base import UpperOntologyBase
from app.kg.graph import Graph
from app.kg.iri import IRI
from app.kg.literal import Literal


class TransformerBase:
    SOURCE_TARGET_RELATION_MAP = {
        ("Deployment", "ReplicaSet"): UpperOntologyBase.HAS_SUBTASK,
        ("ReplicaSet", "Pod"): UpperOntologyBase.MAKES,
        ("DaemonSet", "Pod"): UpperOntologyBase.MAKES,
        ("StatefullSet", "Pod"): UpperOntologyBase.MAKES,
        ("Job", "Pod"): UpperOntologyBase.MAKES,
        ("Pod", "Container"): UpperOntologyBase.HAS_SUBRESOURCE,
    }

    RESOURCES = {"Pod", "Container"}

    RESOURCE_TYPE_MAP = {
        "Deployment": UpperOntologyBase.ASSIGNED_TASK,
        "ReplicaSet": UpperOntologyBase.ASSIGNED_TASK,
        "DaemonSet": UpperOntologyBase.ASSIGNED_TASK,
        "StatefullSet": UpperOntologyBase.ASSIGNED_TASK,
        "Job": UpperOntologyBase.ASSIGNED_TASK,
        "Pod": UpperOntologyBase.WORK_PRODUCING_RESOURCE,
        "Container": UpperOntologyBase.WORK_PRODUCING_RESOURCE,
    }

    CLUSTER_PREFIX = "cluster"
    K8S_PREFIX = "k8s"

    HAS_NAME = IRI(K8S_PREFIX, "hasName")
    HAS_CONTAINER_ID = IRI(K8S_PREFIX, "hasContainerID")
    HAS_CONTAINER_NAME = IRI(K8S_PREFIX, "hasContainerName")

    source: Dict[str, Any]
    sink: Graph

    def __init__(self, source: Dict[str, Any], sink: Graph):
        self.source = source
        self.sink = sink

    def transform(self, context: TransformationContext) -> None:
        raise NotImplementedError

    def get_reference_id(self, reference: Dict[str, Any]) -> Tuple[IRI, str]:
        name = reference["name"]
        resource_type = reference["kind"]
        resource_id = IRI(self.CLUSTER_PREFIX, name)
        return resource_id, resource_type

    def write_tuple(self, name: IRI, property: IRI, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.add_property(
                name,
                property,
                Literal(self.escape(f"{match.value}"), Literal.TYPE_STRING),
            )

    def write_meta_tuple(self, name: IRI, property: IRI, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.add_meta_property(
                name,
                property,
                Literal(self.escape(f"{match.value}"), Literal.TYPE_STRING),
            )

    def write_tuple_from(
        self, source: Dict[str, Any], name: IRI, property: IRI, query: str
    ) -> None:
        for match in parse(query).find(source):
            self.sink.add_property(
                name,
                property,
                Literal(self.escape(f"{match.value}"), Literal.TYPE_STRING),
            )

    def write_tuple_list(self, name: IRI, property: IRI, query: str) -> None:
        for label, value in parse(query).find(self.source)[0].value.items():
            self.sink.add_property(
                name,
                property,
                Literal(self.escape(f"{label}:{value}"), Literal.TYPE_STRING),
            )

    def write_collection(self, name: IRI, property: IRI, query: str) -> None:
        subjects: Set[Literal] = set()
        found = parse(query).find(self.source)
        if len(found) == 0:
            return
        for label, value in found[0].value.items():
            subjects.add(
                Literal(
                    self.escape(f"{self.normalize(label)}:{self.normalize(value)}"),
                    Literal.TYPE_STRING,
                )
            )
        self.sink.add_property_collection(name, property, subjects)

    def escape(self, token: str) -> str:
        return token.replace('"', '\\"')

    def normalize(self, value: str) -> str:
        return re.sub('["\n]', "", value)

    def get_id(self) -> IRI:
        name = parse("$.metadata.name").find(self.source)[0].value
        resource_id = IRI(self.CLUSTER_PREFIX, name)
        return resource_id

    def get_pod_id(self) -> IRI:
        name = parse("$.metadata.name").find(self.source)[0].value
        namespace = parse("$.metadata.namespace").find(self.source)[0].value
        return IRI(self.CLUSTER_PREFIX, namespace).dot(name)

    def get_node_id(self, node_resource: Dict[str, Any]) -> IRI:
        name = parse("$.metadata.name").find(node_resource)[0].value
        resource_id = IRI(self.CLUSTER_PREFIX, name)
        return resource_id

    def get_str_value(self, query: str) -> Optional[str]:
        for match in parse(query).find(self.source):
            return str(match.value)
        return None

    def get_int_value(self, query: str) -> Optional[int]:
        for match in parse(query).find(self.source):
            return int(match.value)
        return None

    def add_references(self, node_id: IRI, target_kind: str) -> None:
        references_match = parse("$.metadata.ownerReferences").find(self.source)
        if len(references_match) == 0:
            return
        for reference_match in references_match[0].value:
            reference, src_kind = self.get_reference_id(reference_match)
            src_type = (
                self.RESOURCE_TYPE_MAP.get(src_kind) or UpperOntologyBase.ASSIGNED_TASK
            )
            relation = (
                self.SOURCE_TARGET_RELATION_MAP.get((src_kind, target_kind))
                or UpperOntologyBase.MAKES
            )
            self.sink.add_relation(reference, relation, node_id)
            self.sink.add_meta_property(reference, Graph.RDF_TYPE_IRI, src_type)
            self.sink.add_property(
                reference,
                UpperOntologyBase.HAS_DESCRIPTION,
                Literal(src_kind, Literal.TYPE_STRING),
            )

    def add_str_property(self, subject: IRI, property: IRI, query: str) -> None:
        for match in parse(query).find(self.source):
            self.sink.add_property(
                subject,
                property,
                Literal(match.value, Literal.TYPE_STRING),
            )
