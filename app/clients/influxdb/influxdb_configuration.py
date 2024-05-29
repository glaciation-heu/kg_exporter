from typing import List

from dataclasses import dataclass


@dataclass
class QueryConfig:
    query: str
    measurement_name: str
    source: str
    property: str
    unit: str
    is_aggregated: bool


@dataclass
class InfluxDBConfiguration:
    url: str
    token: str
    org: str
    pod_queries: List[QueryConfig]
    node_queries: List[QueryConfig]
    workload_queries: List[QueryConfig]
