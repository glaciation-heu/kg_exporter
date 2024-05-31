from typing import List

from app.clients.influxdb.metric_value import MetricValue
from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.types import DKGSlice, KGSliceId
from app.kg.inmemory_graph import InMemoryGraph


class KGSliceAssembler:
    def assemble(
        self,
        now: int,
        slice_id: KGSliceId,
        cluster_snapshot: ResourceSnapshot,
        pod_metrics: List[MetricValue],
        node_metrics: List[MetricValue],
        workload_metrics: List[MetricValue],
    ) -> DKGSlice:
        graph = InMemoryGraph()
        slice = DKGSlice(slice_id, graph, now)
        return slice
