import asyncio
from unittest import TestCase

from app.clients.prometheus.mock_prometheus_client import MockPrometheusClient
from app.core.repository.metric_repository import MetricRepository
from app.core.repository.types import MetricQuery, ResultParserId
from app.core.types import MetricValue


class MetricRepositoryTest(TestCase):
    client: MockPrometheusClient
    repository: MetricRepository

    def setUp(self) -> None:
        self.client = MockPrometheusClient()
        self.repository = MetricRepository(self.client)

    def test_query_one(self) -> None:
        expected = MetricValue("id", "resource", 100500, 42.0)
        self.client.mock_query("test_query", [expected])
        now = 1
        query = MetricQuery(
            measurement_id="measurement",
            subresource=None,
            source="source",
            query="test_query",
            unit="bytes",
            property="property",
            result_parser=ResultParserId.PROMETHEUS_PARSER,
        )

        actual = asyncio.run(self.repository.query_one(now, query))
        self.assertEqual([(query, expected)], actual)

    def test_query_many(self) -> None:
        expected1 = MetricValue("id1", "pod1", 100500, 41.0)
        expected2 = MetricValue("id2", "node1", 100500, 42.0)
        expected3 = MetricValue("id3", "deployment1", 100500, 43.0)
        self.client.mock_query("test_query1", [expected1])
        self.client.mock_query("test_query2", [expected2])
        self.client.mock_query("test_query3", [expected3])
        now = 1
        query1 = MetricQuery(
            measurement_id="measurement",
            subresource=None,
            source="source",
            unit="bytes",
            property="property",
            query="test_query1",
            result_parser=ResultParserId.PROMETHEUS_PARSER,
        )
        query2 = MetricQuery(
            measurement_id="measurement",
            subresource=None,
            source="source",
            query="test_query2",
            unit="bytes",
            property="property",
            result_parser=ResultParserId.PROMETHEUS_PARSER,
        )
        query3 = MetricQuery(
            measurement_id="measurement",
            subresource=None,
            source="source",
            query="test_query3",
            unit="bytes",
            property="property",
            result_parser=ResultParserId.PROMETHEUS_PARSER,
        )

        actual = asyncio.run(self.repository.query_many(now, [query1, query2, query3]))
        self.assertEqual(
            [(query1, expected1), (query2, expected2), (query3, expected3)], actual
        )
