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
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT ?resource ?statusValue
            WHERE {{
                {{
                    SELECT ?graphURI WHERE {{
                        GRAPH ?graphURI {{}}
                        FILTER regex(str(?graphURI), "^timestamp:")
                    }}
                    ORDER BY DESC(xsd:integer(replace(str(?graphURI), "^timestamp:", "")))
                    LIMIT 1
                }}
                GRAPH ?graphURI {{
                    SELECT ?pod ?resource ?statusValue WHERE {{
                        ?resource rdf:type <glc:WorkProducingResource>.
                        ?resource <glc:hasDescription> "{resource_type}".
                        ?resource <glc:hasStatus> ?status.
                        ?status <glc:hasDescription> ?statusValue.
                        FILTER NOT EXISTS{{ ?status <glc:hasDescription> 'Succeeded' }}.
                        FILTER NOT EXISTS{{ ?status <glc:hasDescription> 'Failed' }}.
                        FILTER NOT EXISTS{{ ?status <glc:hasDescription> 'Unknown' }}.
                        FILTER NOT EXISTS{{ ?status <glc:hasDescription> 'NotReady' }}.
                        FILTER NOT EXISTS{{ ?status <glc:hasDescription> 'terminated' }}.
                    }}
                }}
            }}
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
