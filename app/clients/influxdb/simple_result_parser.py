from typing import Any, Dict, List

from app.clients.influxdb.query_result_parser import QueryResultParser
from app.core.metric_value import MetricValue


class SimpleResultParser(QueryResultParser):
    METRICID_FIELD: str = "metric_id"
    RESOURCEID_FIELD: str = "resource_id"
    TIMESTAMP_FIELD: str = "timestamp"
    VALUE_FIELD: str = "value"

    def parse(self, row: Dict[str, Any]) -> List[MetricValue]:
        return [
            MetricValue(
                row[self.METRICID_FIELD],
                row[self.RESOURCEID_FIELD],
                self.get_timestamp(row[self.TIMESTAMP_FIELD]),
                self.get_float(row[self.VALUE_FIELD]),
            )
        ]
