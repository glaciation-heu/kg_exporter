from typing import List, Tuple

from app.core.metric_repository import MetricQuery
from app.core.metric_value import MetricValue
from app.k8s_transform.transformation_context import TransformationContext
from app.kg.graph import Graph


class MetricToGraphTransformerBase:
    source: List[Tuple[MetricQuery, MetricValue]]
    sink: Graph

    def __init__(self, metrics: List[Tuple[MetricQuery, MetricValue]], sink: Graph):
        self.metrics = metrics
        self.sink = sink

    def transform(self, context: TransformationContext) -> None:
        raise NotImplementedError