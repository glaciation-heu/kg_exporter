from typing import TypeAlias

from dataclasses import dataclass

MetricId: TypeAlias = str
ResourceId: TypeAlias = str


@dataclass
class MetricValue:
    metric_id: MetricId
    resource_id: ResourceId
    timestamp: int
    value: float
