from typing import List

from dataclasses import dataclass, field

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.metric_value import MetricValue
from app.kg.graph import Graph


@dataclass(frozen=True)
class KGSliceId:
    node_ip: str
    port: int

    def get_host_port(self) -> str:
        return f"{self.node_ip}:{self.port}"


@dataclass
class DKGSlice:
    slice_id: KGSliceId
    graph: Graph
    timestamp: int


@dataclass
class MetricSnapshot:
    pod_metrics: List[MetricValue] = field(default_factory=list)
    node_metrics: List[MetricValue] = field(default_factory=list)
    workload_metrics: List[MetricValue] = field(default_factory=list)


@dataclass
class SliceInputs:
    resource: ResourceSnapshot
    metrics: MetricSnapshot
