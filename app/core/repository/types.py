from typing import Any, Optional

import importlib
from dataclasses import dataclass
from enum import StrEnum


class ResultParserId(StrEnum):
    SIMPLE_RESULT_PARSER = (
        "app.clients.influxdb.simple_result_parser.SimpleResultParser"
    )

    def get_by_name(self) -> Any:
        if self.name == "SIMPLE_RESULT_PARSER":
            return self.instantiate(self.value)
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
