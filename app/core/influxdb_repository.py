from typing import List

import asyncio
from dataclasses import dataclass
from enum import StrEnum

from app.clients.influxdb.influxdb_client import InfluxDBClient
from app.clients.influxdb.metric_value import MetricValue
from app.clients.influxdb.query_result_parser import QueryResultParser
from app.clients.influxdb.simple_result_parser import SimpleResultParser


class ResultParserId(StrEnum):
    SIMPLE_RESULT_PARSER = "SimpleResultParser"

    def get_by_name(self) -> QueryResultParser:
        if self.name == "SIMPLE_RESULT_PARSER":
            return SimpleResultParser()
        else:
            raise Exception(f"Unknown parser for {self}")


@dataclass
class MetricQuery:
    measurement_name: str
    query: str
    result_parser: ResultParserId
    source: str


@dataclass
class Metric:
    identifier: str
    kind: str
    measurement_name: str
    metric_name: str
    value: float
    timestamp: int
    source: str


class InfluxDBRepository:
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
