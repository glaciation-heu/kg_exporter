import datetime
from unittest import TestCase

from dateutil.tz import tzutc

from app.clients.influxdb.metric_value import MetricValue
from app.clients.influxdb.simple_result_parser import SimpleResultParser


class SimpleResultParserTest(TestCase):
    def test_parse(self) -> None:
        parser = SimpleResultParser()

        row = {
            "result": "_result",
            "table": 0,
            "_start": datetime.datetime(2024, 5, 31, 7, 53, 2, 452746, tzinfo=tzutc()),
            "_stop": datetime.datetime(2024, 5, 31, 8, 13, 2, 452746, tzinfo=tzutc()),
            "timestamp": datetime.datetime(2024, 5, 31, 8, 0, tzinfo=tzutc()),
            "value": 26237685760.0,
            "_field": "node_memory_MemFree_bytes",
            "_measurement": "prometheus_remote_write",
            "app_kubernetes_io_component": "metrics",
            "app_kubernetes_io_instance": "monitoring-stack",
            "app_kubernetes_io_managed_by": "Helm",
            "app_kubernetes_io_name": "prometheus-node-exporter",
            "app_kubernetes_io_part_of": "prometheus-node-exporter",
            "app_kubernetes_io_version": "1.7.0",
            "helm_sh_chart": "prometheus-node-exporter-4.25.0",
            "host": "telegraf-polling-service",
            "instance": "10.14.1.160:9100",
            "job": "kubernetes-service-endpoints",
            "namespace": "monitoring",
            "identifier": "glaciation-testm1w5-master01",
            "service": "monitoring-stack-prometheus-node-exporter",
        }
        actual = parser.parse(row)

        self.assertEqual(
            MetricValue("glaciation-testm1w5-master01", 1717142400000, 26237685760.0),
            actual,
        )
