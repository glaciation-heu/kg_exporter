from typing import List

from app.clients.influxdb.query_result_parser import QueryResultParser
from app.core.metric_value import MetricValue


class MetricStoreClient:
    async def query(
        self, query: str, result_parser: QueryResultParser
    ) -> List[MetricValue]:
        raise NotImplementedError
