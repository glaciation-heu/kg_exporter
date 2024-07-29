from typing import List, Tuple

import asyncio

from app.core.repository.metricstore_client import MetricStoreClient
from app.core.repository.query_settings import QuerySettings
from app.core.repository.types import MetricQuery
from app.core.types import MetricSnapshot, MetricValue


class MetricRepository:
    client: MetricStoreClient

    def __init__(self, client: MetricStoreClient):
        self.client = client

    async def metric_snapshot(self, now: int, queries: QuerySettings) -> MetricSnapshot:
        (pod_metrics, node_metrics) = await asyncio.gather(
            self.query_many(now, queries.pod_queries),
            self.query_many(now, queries.node_queries),
        )
        return MetricSnapshot(pod_metrics, node_metrics)

    async def query_many(
        self, now: int, queries: List[MetricQuery]
    ) -> List[Tuple[MetricQuery, MetricValue]]:
        query_futures = [self.query_one(now, query) for query in queries]
        query_results: List[
            List[Tuple[MetricQuery, MetricValue]]
        ] = await asyncio.gather(*query_futures)
        return [element for elements in query_results for element in elements]

    async def query_one(
        self, now: int, query: MetricQuery
    ) -> List[Tuple[MetricQuery, MetricValue]]:
        result_parser = query.result_parser.get_by_name()
        query_str = query.query.replace("{{now}}", str(now / 1000))
        results = await self.client.query(query_str, result_parser)
        return [(query, result) for result in results]
