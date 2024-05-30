from typing import Any, Dict

from app.clients.influxdb.metric_value import MetricValue
from app.clients.influxdb.query_result_parser import QueryResultParser


class SimpleResultParser(QueryResultParser):
    IDENTIFIER_FIELD: str = "identifier"
    TIMESTAMP_FIELD: str = "timestamp"
    VALUE_FIELD: str = "value"

    def parse(self, row: Dict[str, Any]) -> MetricValue:
        return MetricValue(
            row[self.IDENTIFIER_FIELD],
            self.get_timestamp(row[self.TIMESTAMP_FIELD]),
            self.get_float(row[self.VALUE_FIELD]),
        )
