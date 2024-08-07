from typing import Any, Dict, List

from datetime import datetime

from app.core.types import MetricValue


class QueryResultParser:
    def get_timestamp(self, dt: Any) -> int:
        if isinstance(dt, int) or isinstance(dt, float):
            return int(dt)
        elif isinstance(dt, datetime):
            return int(dt.timestamp() * 1000)
        else:
            raise Exception(
                f"Unable to convert value '{dt}' to timestamp. Unknown type {type(dt)}."
            )

    def get_float(self, value: Any) -> float:
        if isinstance(value, int) or isinstance(value, float):
            return value
        else:
            raise Exception(
                f"Unable to convert value '{value}' to float. Unknown type {type(value)}."
            )

    def parse(self, row: Dict[str, Any]) -> List[MetricValue]:
        raise NotImplementedError
