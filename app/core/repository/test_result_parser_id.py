from unittest import TestCase

from app.core.repository.types import ResultParserId


class ResultParserIdTest(TestCase):
    def test_get_by_name(self) -> None:
        parser = ResultParserId.PROMETHEUS_PARSER.get_by_name()

        self.assertEqual(type(parser).__name__, "PrometheusResultParser")
