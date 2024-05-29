from typing import Set

from dataclasses import dataclass, field

from app.clients.influxdb.influxdb_client import InfluxDBClient


@dataclass
class Metric:
    measurement_name: str
    metric_name: str
    value: float
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

    async def fetch(self) -> MetricsSnapshot:
        # query_api = self.client.query_api()
        # query = ""
        # result = await query_api.query(query)
        return MetricsSnapshot()
