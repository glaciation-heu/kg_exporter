from typing import TypeAlias

from dataclasses import dataclass

MetricId: TypeAlias = str


@dataclass
class MetricValue:
    metric_id: MetricId
    timestamp: int
    value: float
