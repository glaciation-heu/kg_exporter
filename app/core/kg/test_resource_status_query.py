from unittest import TestCase

from app.core.kg.resource_status_query import (
    ResourceStatus,
    ResourceStatusQuery,
    ResourceType,
)
from app.kg.iri import IRI
from app.kg.literal import Literal


class ResourceStatusQueryTest(TestCase):
    def test_get_query(self) -> None:
        query = ResourceStatusQuery(ResourceType.POD)
        self.assertEqual(
            """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?subject ?statusValue
            WHERE {
                ?subject rdf:type <glc:WorkProducingResource>.
                ?subject <glc:hasDescription> "Pod".
                ?subject <glc:hasStatus> ?status.
                ?status <glc:hasDescription> ?statusValue.
                FILTER NOT EXISTS{ ?status <glc:hasDescription> 'Succeeded' }.
                FILTER NOT EXISTS{ ?status <glc:hasDescription> 'Failed' }.
                FILTER NOT EXISTS{ ?status <glc:hasDescription> 'Unknown' }.
                FILTER NOT EXISTS{ ?status <glc:hasDescription> 'NotReady' }.
                FILTER NOT EXISTS{ ?status <glc:hasDescription> 'terminated' }.
            }
        """,
            query.get_query(),
        )

    def test_parse_results(self) -> None:
        query = ResourceStatusQuery(ResourceType.POD)
        actual = query.parse_results(
            [
                {
                    "resource": IRI(
                        "https://kubernetes.local/",
                        "uc2.uc2-workload-service-28725480-cz9mg",
                    ),
                    "statusValue": Literal("running", Literal.TYPE_STRING),
                },
                {
                    "resource": IRI("https://kubernetes.local", "vault.vault-0"),
                    "statusValue": Literal("running", Literal.TYPE_STRING),
                },
            ]
        )
        self.assertEqual(
            actual,
            [
                ResourceStatus(
                    identifier=IRI(
                        "https://kubernetes.local/",
                        "uc2.uc2-workload-service-28725480-cz9mg",
                    ),
                    status="running",
                    resource_type=ResourceType.POD,
                ),
                ResourceStatus(
                    identifier=IRI("https://kubernetes.local", "vault.vault-0"),
                    status="running",
                    resource_type=ResourceType.POD,
                ),
            ],
        )
