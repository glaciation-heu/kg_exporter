from typing import Any, Optional

import importlib
from dataclasses import dataclass
from enum import StrEnum


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


@dataclass
class MetricQuery:
    measurement_id: str
    subresource: Optional[str]
    source: str
    unit: str
    property: str
    query: str
    result_parser: ResultParserId
