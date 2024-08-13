import json
from io import StringIO

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.kg.kg_snapshot import KGSnapshot
from app.core.kg.resource_status_query import ResourceStatus
from app.kg.inmemory_graph import InMemoryGraph
from app.kg.iri import IRI
from app.serialize.jsonld_serializer import JsonLDSerialializer
from app.transform.k8s.resource_termination_transformer import (
    ResourceTerminationTransformer,
)
from app.transform.k8s.test_base import TransformBaseTest
from app.transform.k8s.transformation_context import TransformationContext


class ResourceTerminationTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_empty(self):
        self.transform_jsonld(ResourceSnapshot(), KGSnapshot(), "termination.empty")

    def test_basic(self):
        resources = ResourceSnapshot(
            nodes=[
                {
                    "metadata": {
                        "name": "glaciation-test-master01",
                    }
                }
            ],
            pods=[
                {
                    "metadata": {
                        "name": "kube-flannel-ds-848v8",
                        "namespace": "kube-flannel",
                    },
                    "status": {
                        "containerStatuses": [
                            {
                                "state": {
                                    "running": {"startedAt": "2023-12-11T11:10:16Z"}
                                }
                            }
                        ],
                        "initContainerStatuses": [
                            {
                                "state": {
                                    "terminated": {
                                        "finishedAt": "2023-12-11T11:10:14Z",
                                        "startedAt": "2023-12-11T11:10:14Z",
                                    }
                                }
                            }
                        ],
                        "phase": "Running",
                        "startTime": "2023-10-20T11:01:50Z",
                    },
                }
            ],
        )
        existing_metadata = KGSnapshot(
            nodes=[
                ResourceStatus(
                    IRI("cluster", "glaciation-testm1w5-worker02"),
                    "Ready",
                    "KubernetesWorkerNode",
                )
            ],
            pods=[
                ResourceStatus(
                    IRI(
                        "cluster",
                        "kube-system.coredns-787d4945fb-bfv2k",
                    ),
                    "running",
                    "Pod",
                )
            ],
            containers=[
                ResourceStatus(
                    IRI(
                        "cluster",
                        "kube-system.coredns-787d4945fb-bfv2k.coredns",
                    ),
                    "running",
                    "Container",
                )
            ],
        )
        self.transform_jsonld(resources, existing_metadata, "termination.basic")

    def transform_jsonld(
        self, resources: ResourceSnapshot, existing_metadata: KGSnapshot, file_id: str
    ) -> None:
        node_jsonld = self.load_jsonld(file_id)

        buffer = StringIO()
        graph = InMemoryGraph()
        context = TransformationContext(123)
        transformer = ResourceTerminationTransformer(
            resources, existing_metadata, graph
        )
        transformer.transform(context)
        JsonLDSerialializer(self.get_jsonld_config()).write(buffer, graph)
        self.assertEqual(json.loads(buffer.getvalue()), node_jsonld)
