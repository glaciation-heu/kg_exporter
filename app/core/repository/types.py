from typing import Any, Optional

import importlib
from enum import StrEnum

from pydantic_settings import BaseSettings


class ResultParserId(StrEnum):
    PROMETHEUS_PARSER = "PROMETHEUS_PARSER"

    def get_by_name(self) -> Any:
        if self.name == ResultParserId.PROMETHEUS_PARSER:
            return self.instantiate(
                "app.clients.prometheus.prometheus_result_parser.PrometheusResultParser"
            )
        else:
            raise Exception(f"Unknown parser for {self}")

    def instantiate(self, clazz: str) -> Any:
        idx = clazz.rfind(".")
        module, class_name = clazz[:idx], clazz[idx + 1 :]
        ClassObj = getattr(importlib.import_module(module), class_name)
        return ClassObj()


class Aggregation(BaseSettings):
    period_seconds: int
    function: str


class MetricQuery(BaseSettings):
    measurement_id: str
    subresource: Optional[str] = None
    aggregation: Optional[Aggregation] = None
    source: str
    unit: str
    property: str
    query: str
    result_parser: ResultParserId
