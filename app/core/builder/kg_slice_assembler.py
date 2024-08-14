from typing import Any, Dict, List, Type

from urllib.parse import urlparse

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.kg.kg_snapshot import KGSnapshot
from app.core.types import DKGSlice, KGSliceId, MetricSnapshot, SliceInputs
from app.kg.graph import Graph
from app.kg.inmemory_graph import InMemoryGraph
from app.transform.k8s.cluster_transformer import ClusterToRDFTransformer
from app.transform.k8s.node_transformer import NodesToRDFTransformer
from app.transform.k8s.pod_transformer import PodToRDFTransformer
from app.transform.k8s.resource_termination_transformer import (
    ResourceTerminationTransformer,
)
from app.transform.k8s.workload_transformer import WorkloadToRDFTransformer
from app.transform.metrics.node_metric_transformer import NodeMetricToGraphTransformer
from app.transform.metrics.pod_metric_transformer import PodMetricToGraphTransformer
from app.transform.transformation_context import TransformationContext
from app.transform.transformer_base import TransformerBase


class KGSliceAssembler:
    def assemble(
        self,
        now: int,
        slice_id: KGSliceId,
        inputs: SliceInputs,
        existing_metadata: KGSnapshot,
    ) -> DKGSlice:
        sink = InMemoryGraph()

        self.transform_resources(now, inputs.resource, sink)
        self.transform_metrics(now, inputs.metrics, sink)
        self.terminate_existing_resources(now, inputs.resource, existing_metadata, sink)
        context = self.get_context(inputs.resource.versions_info)

        slice = DKGSlice(slice_id, sink, context, now)
        return slice

    def transform_resources(
        self, now: int, snapshot: ResourceSnapshot, sink: Graph
    ) -> None:
        context = TransformationContext(now)
        self.transform_cluster(sink, snapshot.nodes, snapshot.cluster, context)
        self.transform_resource(sink, snapshot.nodes, context, NodesToRDFTransformer)
        self.transform_resource(sink, snapshot.pods, context, PodToRDFTransformer)
        self.transform_resource(
            sink, snapshot.daemonsets, context, WorkloadToRDFTransformer
        )
        self.transform_resource(
            sink, snapshot.deployments, context, WorkloadToRDFTransformer
        )
        self.transform_resource(
            sink, snapshot.replicasets, context, WorkloadToRDFTransformer
        )
        self.transform_resource(sink, snapshot.jobs, context, WorkloadToRDFTransformer)
        self.transform_resource(
            sink, snapshot.statefullsets, context, WorkloadToRDFTransformer
        )

    def transform_cluster(
        self,
        sink: Graph,
        nodes: List[Dict[str, Any]],
        cluster_info: Dict[str, Any],
        context: TransformationContext,
    ) -> None:
        transformer = ClusterToRDFTransformer(cluster_info, nodes, sink)
        transformer.transform(context)

    def transform_resource(
        self,
        sink: Graph,
        nodes: List[Dict[str, Any]],
        context: TransformationContext,
        transformer_cls: Type[TransformerBase],
    ) -> None:
        for node in nodes:
            transformer = transformer_cls(node, sink)
            transformer.transform(context)

    def transform_metrics(
        self,
        now: int,
        snapshot: MetricSnapshot,
        sink: Graph,
    ) -> None:
        context = TransformationContext(now)
        node_transformer = NodeMetricToGraphTransformer(snapshot.node_metrics, sink)
        node_transformer.transform(context)
        pod_transformer = PodMetricToGraphTransformer(snapshot.pod_metrics, sink)
        pod_transformer.transform(context)

    def get_context(self, versions_info: Dict[str, Any]) -> Dict[str, Any]:
        server_address_by_client_cid_rs_list = (
            versions_info.get("server_address_by_client_cid_rs") or []
        )
        server_address_url = "https://kubernetes.local/"
        for server_address_by_client_cid_rs in server_address_by_client_cid_rs_list:
            server_address = server_address_by_client_cid_rs.get("server_address")
            if server_address:
                server_address_url = server_address
                break

        context = {
            "k8s": "http://glaciation-project.eu/model/k8s/",
            "glc": "https://glaciation-heu.github.io/models/reference_model.turtle",
            "cluster": self.unify_url(server_address_url),
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
        return context

    def unify_url(self, server_address_url: str) -> str:
        parse_result = urlparse(server_address_url)
        if not parse_result.scheme:
            return f"https://{server_address_url}/"
        else:
            return server_address_url

    def terminate_existing_resources(
        self,
        now: int,
        resources: ResourceSnapshot,
        existing_metadata: KGSnapshot,
        sink: Graph,
    ) -> None:
        context = TransformationContext(now)
        transformer = ResourceTerminationTransformer(resources, existing_metadata, sink)
        transformer.transform(context)
