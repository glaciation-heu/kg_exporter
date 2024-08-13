from typing import Dict, List

from dataclasses import dataclass
from enum import StrEnum

from app.core.kg.kg_query import KGQuery
from app.kg.id_base import IdBase


@dataclass
class ResourceStatus:
    identifier: str
    status: str
    resource_type: str


class ResourceType(StrEnum):
    NODE = "KubernetesWorkerNode"
    POD = "Pod"
    CONTAINER = "Container"


class ResourceStatusQuery(KGQuery[List[ResourceStatus]]):
    query: str
    resource_type: ResourceType

    def __init__(self, resource_type: ResourceType):
        self.resource_type = resource_type
        self.query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?resource ?statusValue
            WHERE {{
                ?resource rdf:type <glc:WorkProducingResource>.
                ?resource <glc:hasDescription> "{resource_type}".
                ?resource <glc:hasStatus> ?status.
                ?status <glc:hasDescription> ?statusValue
            }}
        """

    def get_query(self) -> str:
        return self.query

    def parse(self, query_result: List[Dict[str, IdBase]]) -> List[ResourceStatus]:
        nodes = []
        for result in query_result:
            identifier = result["resource"].get_value()
            status = result["statusValue"].get_value()
            node = ResourceStatus(
                identifier=identifier, status=status, resource_type=self.resource_type
            )
            nodes.append(node)
        return nodes
