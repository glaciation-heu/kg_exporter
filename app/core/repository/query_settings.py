from typing import List

from pydantic_settings import BaseSettings

from app.core.repository.types import MetricQuery


class QuerySettings(BaseSettings):
    pod_queries: List[MetricQuery] = []
    node_queries: List[MetricQuery] = []
