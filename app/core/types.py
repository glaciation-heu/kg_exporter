from typing import List, Set, Tuple

import urllib.parse
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

    @staticmethod
    def from_host_port(host_and_port: str) -> "KGSliceId":
        result = urllib.parse.urlsplit(f"//{host_and_port}")
        return KGSliceId(str(result.hostname), result.port or 80)


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
    # TODO remove workload_metrics
    workload_metrics: List[Tuple[MetricQuery, MetricValue]] = field(
        default_factory=list
    )

    def get_metric_names(self) -> Set[str]:
        names: Set[str] = set()
        names = {*names, *{resource[1].metric_id for resource in self.pod_metrics}}
        names = {*names, *{resource[1].metric_id for resource in self.node_metrics}}
        return names

    def get_node_metrics_by_resource(
        self, resource_name: str
    ) -> List[Tuple[MetricQuery, MetricValue]]:
        return [
            metric
            for metric in self.node_metrics
            if metric[1].resource_id == resource_name
        ]

    def get_pod_metrics_by_resource(
        self, resource_name: str
    ) -> List[Tuple[MetricQuery, MetricValue]]:
        return [
            metric
            for metric in self.pod_metrics
            if metric[1].resource_id == resource_name
        ]


@dataclass
class SliceInputs:
    resource: ResourceSnapshot
    metrics: MetricSnapshot
