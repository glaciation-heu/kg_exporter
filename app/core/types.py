from typing import List, Set

from dataclasses import dataclass, field

from app.core.influxdb_repository import Metric, MetricQuery
from app.kg.graph import Graph


@dataclass
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
class MetricsSnapshot:
    pod_metrics: Set[Metric] = field(default_factory=set)
    node_metrics: Set[Metric] = field(default_factory=set)
    deployment_metrics: Set[Metric] = field(default_factory=set)


@dataclass
class QueryOptions:
    pod_queries: List[MetricQuery] = field(default_factory=list)
    node_queries: List[MetricQuery] = field(default_factory=list)
    workload_queries: List[MetricQuery] = field(default_factory=list)
