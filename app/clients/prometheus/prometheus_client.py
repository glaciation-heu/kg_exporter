from typing import List

from aioprometheus_api_client import PrometheusConnect

from app.clients.influxdb.metricstore_client import MetricStoreClient
from app.clients.influxdb.query_result_parser import QueryResultParser
from app.clients.prometheus.prometheus_client_settings import PrometheusClientSettings
from app.core.metric_value import MetricValue


class PrometheusClient(MetricStoreClient):
    settings: PrometheusClientSettings
    connect: PrometheusConnect

    def __init__(self, settings: PrometheusClientSettings):
        self.settings = settings
        self.connect = PrometheusConnect(url=self.settings.url, disable_ssl=True)

    async def query(
        self, query: str, result_parser: QueryResultParser
    ) -> List[MetricValue]:
        metrics: List[MetricValue] = []
        results = await self.connect.async_custom_query(query)
        for result in results:
            parsed = result_parser.parse(result)
            metrics.extend(parsed)
        return metrics
