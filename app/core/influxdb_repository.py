from typing import List, Set

from dataclasses import dataclass, field

from app.clients.influxdb.influxdb_client import InfluxDBClient


@dataclass
class MetricQuery:
    measurement_name: str
    query: str
    result_parser: str
    source: str


@dataclass
class QueryOptions:
    pod_metric_queries: List[MetricQuery]
    node_metric_queries: List[MetricQuery]
    workload_metric_queries: List[MetricQuery]


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
class MetricsSnapshot:
    pod_metrics: Set[Metric] = field(default_factory=set)
    node_metrics: Set[Metric] = field(default_factory=set)
    deployment_metrics: Set[Metric] = field(default_factory=set)


class InfluxDBRepository:
    client: InfluxDBClient

    def __init__(self, client: InfluxDBClient):
        self.client = client

    async def fetch(
        self, timestamp: int, query_options: QueryOptions
    ) -> MetricsSnapshot:
        # query_api = self.client.query_api()
        # query = ""
        # result = await query_api.query(query)
        return MetricsSnapshot()
