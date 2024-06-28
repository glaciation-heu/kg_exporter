from typing import Dict, List

from app.core.repository.metricstore_client import MetricStoreClient
from app.core.repository.query_result_parser import QueryResultParser
from app.core.types import MetricValue


class MockPrometheusClient(MetricStoreClient):
    results: Dict[str, List[MetricValue]]

    def __init__(self):
        self.results = dict()

    def mock_query(self, query: str, client_response: List[MetricValue]) -> None:
        self.results[query] = client_response

    async def query(self, query: str, _: QueryResultParser) -> List[MetricValue]:
        return self.results.get(query) or []
