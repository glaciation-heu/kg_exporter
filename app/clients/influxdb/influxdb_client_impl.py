from typing import List

from influxdb_client.client.flux_table import TableList
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from app.clients.influxdb.influxdb_settings import InfluxDBSettings
from app.core.repository.metricstore_client import MetricStoreClient
from app.core.repository.query_result_parser import QueryResultParser
from app.core.types import MetricValue


class InfluxDBClientImpl(MetricStoreClient):
    settings: InfluxDBSettings
    async_client: InfluxDBClientAsync

    def __init__(self, settings: InfluxDBSettings):
        self.settings = settings

    async def query(
        self, query: str, result_parser: QueryResultParser
    ) -> List[MetricValue]:
        async with InfluxDBClientAsync(
            url=self.settings.url,
            token=self.settings.token,
            org=self.settings.org,
            timeout=self.settings.timeout,
        ) as async_client:
            flux_result = await async_client.query_api().query(query)
            return self.parse_response(flux_result, result_parser)

    def parse_response(
        self,
        flux_result: TableList,
        result_parser: QueryResultParser,
    ) -> List[MetricValue]:
        query_results = []
        for table in flux_result:
            for record in table.records:
                query_results.extend(result_parser.parse(record))
        return query_results
