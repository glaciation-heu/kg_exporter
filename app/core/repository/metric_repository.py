from typing import List

import asyncio

from app.core.repository.metricstore_client import MetricStoreClient
from app.core.repository.types import MetricQuery
from app.core.types import MetricValue


class MetricRepository:
    client: MetricStoreClient

    def __init__(self, client: MetricStoreClient):
        self.client = client

    async def query_many(
        self, now: int, queries: List[MetricQuery]
    ) -> List[MetricValue]:
        query_futures = [self.query_one(now, query) for query in queries]
        query_results: List[List[MetricValue]] = await asyncio.gather(*query_futures)
        return [element for elements in query_results for element in elements]

    async def query_one(self, now: int, query: MetricQuery) -> List[MetricValue]:
        result_parser = query.result_parser.get_by_name()
        return await self.client.query(query.query, result_parser)
