from typing import List, Tuple

from dataclasses import dataclass, field

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.metric_repository import MetricQuery
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


# TODO remove
@dataclass
class Metric:
    identifier: str
    kind: str
    measurement_name: str
    metric_name: str
    value: float
    timestamp: int
    source: str


@dataclass
class MetricSnapshot:
    pod_metrics: List[Tuple[MetricQuery, MetricValue]] = field(default_factory=list)
    node_metrics: List[Tuple[MetricQuery, MetricValue]] = field(default_factory=list)
    workload_metrics: List[Tuple[MetricQuery, MetricValue]] = field(
        default_factory=list
    )


@dataclass
class SliceInputs:
    resource: ResourceSnapshot
    metrics: MetricSnapshot
