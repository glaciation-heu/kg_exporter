from typing import List, Optional

import asyncio
from dataclasses import dataclass
from enum import StrEnum

from app.clients.influxdb.influxdb_client import InfluxDBClient
from app.clients.influxdb.query_result_parser import QueryResultParser
from app.clients.influxdb.simple_result_parser import SimpleResultParser
from app.core.metric_value import MetricValue


class ResultParserId(StrEnum):
    SIMPLE_RESULT_PARSER = "SimpleResultParser"

    def get_by_name(self) -> QueryResultParser:
        if self.name == "SIMPLE_RESULT_PARSER":
            return SimpleResultParser()
        else:
            raise Exception(f"Unknown parser for {self}")


@dataclass
class MetricQuery:
    measurement_id: str
    subresource: Optional[str]
    source: str
    unit: str
    property: str
    query: str
    result_parser: ResultParserId


class MetricRepository:
    client: InfluxDBClient

    def __init__(self, client: InfluxDBClient):
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
