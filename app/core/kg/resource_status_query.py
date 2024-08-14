from typing import Dict, List

from dataclasses import dataclass
from enum import StrEnum

from app.core.kg.kg_query import KGQuery
from app.kg.id_base import IdBase
from app.kg.iri import IRI


@dataclass
class ResourceStatus:
    identifier: IRI
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
            SELECT ?status (GROUP_CONCAT(DISTINCT ?statusValue; SEPARATOR=", ") AS ?statuses)
            WHERE {{
                ?subject rdf:type <glc:WorkProducingResource>.
                ?subject <glc:hasDescription> "{resource_type}".
                ?subject <glc:hasStatus> ?status.
                ?status <glc:hasDescription> ?statusValue.
                    MINUS{{ ?status <glc:hasDescription> 'Succeeded' }}.
                    MINUS{{ ?status <glc:hasDescription> 'Failed' }}.
                    MINUS{{ ?status <glc:hasDescription> 'Unknown' }}.
                    MINUS{{ ?status <glc:hasDescription> 'NotReady' }}.
                    MINUS{{ ?status <glc:hasDescription> 'terminated' }}.
            }}
            GROUP BY ?status
        """

    def get_query(self) -> str:
        return self.query

    def parse_results(
        self, query_result: List[Dict[str, IdBase]]
    ) -> List[ResourceStatus]:
        nodes = []
        for result in query_result:
            identifier: IRI = result["resource"]  # type: ignore
            status = result["statusValue"].get_value()
            node = ResourceStatus(
                identifier=identifier, status=status, resource_type=self.resource_type
            )
            nodes.append(node)
        return nodes
