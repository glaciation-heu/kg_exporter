from typing import Any, Dict, List, Optional, Set, Tuple

import re

from jsonpath_ng.ext import parse

from app.kg.graph import Graph
from app.kg.iri import IRI
from app.kg.literal import Literal
from app.transform.k8s.transformation_context import TransformationContext
from app.transform.k8s.upper_ontology_base import UpperOntologyBase
from app.util.quantity import parse_quantity


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
        name = self.source["metadata"]["name"]
        resource_id = IRI(self.CLUSTER_PREFIX, name)
        return resource_id

    def get_pod_id(self) -> IRI:
        name = self.source["metadata"]["name"]
        namespace = self.source["metadata"]["namespace"]
        return IRI(self.CLUSTER_PREFIX, namespace).dot(name)

    def get_node_id(self, node_resource: Dict[str, Any]) -> IRI:
        name = node_resource["metadata"]["name"]
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
        references_matches = self.source["metadata"].get("ownerReferences") or []
        if len(references_matches) == 0:
            return
        for reference_match in references_matches:
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
            self.sink.add_relation(reference, UpperOntologyBase.HAS_ID, reference)
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

    def get_opt_str_value(self, query_path: List[str]) -> Optional[str]:
        if len(query_path) == 0:
            return None
        current: Dict[str, Any] = self.source
        result: Optional[str] = None
        for subpath in query_path:
            next = current.get(subpath)
            if not next:
                return None
            current = next
            if isinstance(next, str):
                result = str(current)
        return result

    def get_opt_struct(self, query_path: List[str]) -> Optional[Dict[str, Any]]:
        if len(query_path) == 0:
            return None
        current: Dict[str, Any] = self.source
        for subpath in query_path:
            next = current.get(subpath)
            if not next:
                return None
            current = next
        return current

    def get_opt_list(self, query_path: List[str]) -> Optional[List[Dict[str, Any]]]:
        if len(query_path) == 0:
            return None
        current: Dict[str, Any] = self.source
        result: List[Dict[str, Any]] = []
        for subpath in query_path:
            next = current.get(subpath)
            if not next:
                return None
            current = next
            result = next
        return result

    def get_opt_int_quantity_value(self, query_path: List[str]) -> Optional[int]:
        if len(query_path) == 0:
            return None
        current: Dict[str, Any] = self.source
        result: Any = "0"
        for subpath in query_path:
            next = current.get(subpath)
            if not next:
                return None
            current = next
            result = next
        return int(parse_quantity(result))

    def get_str_list(self, query_path: List[str]) -> List[str]:
        if len(query_path) == 0:
            return []
        results: List[str] = []
        self.fetch_level([self.source], query_path, 0, results)
        return results

    def fetch_level(
        self,
        current: List[Dict[str, Any]],
        query_path: List[str],
        query_path_i: int,
        result: List[str],
    ) -> None:
        if query_path_i == len(query_path) - 1:
            path = query_path[query_path_i]
            for current_level in current:
                query_result = current_level.get(path)
                if query_result:
                    result.append(query_result)
        else:
            path = query_path[query_path_i]
            for current_level in current:
                next_level = current_level.get(path)
                if next_level:
                    if isinstance(next_level, list):
                        self.fetch_level(
                            next_level, query_path, query_path_i + 1, result
                        )
                    else:
                        self.fetch_level(
                            [next_level], query_path, query_path_i + 1, result
                        )
