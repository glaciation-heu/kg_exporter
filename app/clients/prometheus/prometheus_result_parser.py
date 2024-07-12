from typing import Any, Dict, List

from app.core.repository.query_result_parser import QueryResultParser
from app.core.types import MetricValue


class PrometheusResultParser(QueryResultParser):
    def parse(self, row: Dict[str, Any]) -> List[MetricValue]:
        metric = row.get("metric")
        value = row.get("value")
        if metric and value:
            metric_name = metric.get("__name__") or "undefined"
            resource = metric.get("resource") or "undefined"
            timestamp = int(value[0] * 1000)
            metric_value = float(value[1])
            value = MetricValue(
                metric_name,
                resource,
                timestamp=timestamp,
                value=metric_value,
            )
            return [value]
        else:
            return []
