import asyncio
from unittest import TestCase

from app.clients.influxdb.metric_value import MetricValue
from app.clients.influxdb.mock_infuxdbclient import MockInfluxDBClient
from app.core.influxdb_repository import InfluxDBRepository, MetricQuery, ResultParserId


class InfluxDBRepositoryTest(TestCase):
    client: MockInfluxDBClient
    repository: InfluxDBRepository

    def setUp(self) -> None:
        self.client = MockInfluxDBClient()
        self.repository = InfluxDBRepository(self.client)

    def test_query_one(self) -> None:
        expected = MetricValue("id", 100500, 42.0)
        self.client.mock_query("test_query", [expected])
        now = 1
        query = MetricQuery(
            measurement_name="measurement",
            query="test_query",
            result_parser=ResultParserId.SIMPLE_RESULT_PARSER,
            source="source",
        )

        actual = asyncio.run(self.repository.query_one(now, query))
        self.assertEqual([expected], actual)

    def test_query_many(self) -> None:
        expected1 = MetricValue("id1", 100500, 41.0)
        expected2 = MetricValue("id2", 100500, 42.0)
        expected3 = MetricValue("id3", 100500, 43.0)
        self.client.mock_query("test_query1", [expected1])
        self.client.mock_query("test_query2", [expected2])
        self.client.mock_query("test_query3", [expected3])
        now = 1
        query1 = MetricQuery(
            measurement_name="measurement",
            query="test_query1",
            result_parser=ResultParserId.SIMPLE_RESULT_PARSER,
            source="source",
        )
        query2 = MetricQuery(
            measurement_name="measurement",
            query="test_query2",
            result_parser=ResultParserId.SIMPLE_RESULT_PARSER,
            source="source",
        )
        query3 = MetricQuery(
            measurement_name="measurement",
            query="test_query3",
            result_parser=ResultParserId.SIMPLE_RESULT_PARSER,
            source="source",
        )

        actual = asyncio.run(self.repository.query_many(now, [query1, query2, query3]))
        self.assertEqual([expected1, expected2, expected3], actual)
