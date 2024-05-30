from typing import List

from app.clients.influxdb.metric_value import MetricValue
from app.clients.influxdb.query_result_parser import QueryResultParser


class InfluxDBClient:
    async def query(
        self, query: str, result_parser: QueryResultParser
    ) -> List[MetricValue]:
        raise NotImplementedError
