from typing import Any, Dict, List, Type

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.types import DKGSlice, KGSliceId, MetricSnapshot, SliceInputs
from app.k8s_transform.node_transformer import NodesToRDFTransformer
from app.k8s_transform.pod_transformer import PodToRDFTransformer
from app.k8s_transform.transformation_context import TransformationContext
from app.k8s_transform.transformer_base import TransformerBase
from app.k8s_transform.workload_transformer import WorkloadToRDFTransformer
from app.kg.graph import Graph
from app.kg.inmemory_graph import InMemoryGraph
from app.metric_transform.node_metric_transformer import NodeMetricToGraphTransformer
from app.metric_transform.pod_metric_transformer import PodMetricToGraphTransformer


class KGSliceAssembler:
    def assemble(
        self,
        now: int,
        slice_id: KGSliceId,
        inputs: SliceInputs,
    ) -> DKGSlice:
        sink = InMemoryGraph()

        self.transform_resources(now, inputs.resource, sink)
        self.transform_metrics(now, inputs.metrics, sink)

        slice = DKGSlice(slice_id, sink, now)
        return slice

    def transform_resources(
        self, now: int, snapshot: ResourceSnapshot, sink: Graph
    ) -> None:
        context = TransformationContext(now)
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
