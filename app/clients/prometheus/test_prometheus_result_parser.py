from typing import Any, Dict, List

from unittest import TestCase

from app.clients.prometheus.prometheus_result_parser import PrometheusResultParser
from app.core.types import MetricValue


class PrometheusResultParserTest(TestCase):
    input: List[Dict[str, Any]] = [
        {
            "metric": {
                "__name__": "RAM.Capacity",
                "exported_instance": "glaciation-testm1w5-master01",
                "resource": "10.14.1.160: 9102",
                "job": "kepler",
                "mode": "dynamic",
                "package": "estimator0",
                "source": "trained_power_model",
            },
            "value": [1719489127.684, "23487213.396"],
        },
        {
            "metric": {
                "__name__": "RAM.Capacity",
                "exported_instance": "glaciation-testm1w5-worker01",
                "resource": "10.14.1.161: 9102",
                "job": "kepler",
                "mode": "dynamic",
                "package": "estimator0",
                "source": "trained_power_model",
            },
            "value": [1719489127.684, "4996106.442"],
        },
    ]

    def test_parse(self) -> None:
        parser = PrometheusResultParser()

        actual = parser.parse(self.input[0])

        self.assertEqual(
            [
                MetricValue(
                    "RAM.Capacity",
                    "10.14.1.160: 9102",
                    1719489127684,
                    23487213.396,
                )
            ],
            actual,
        )

        actual = parser.parse(self.input[1])

        self.assertEqual(
            [
                MetricValue(
                    "RAM.Capacity",
                    "10.14.1.161: 9102",
                    1719489127684,
                    4996106.442,
                )
            ],
            actual,
        )
