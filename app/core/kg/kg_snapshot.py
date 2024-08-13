from typing import List

from dataclasses import dataclass

from app.core.kg.resource_status_query import ResourceStatus


@dataclass
class KGSnapshot:
    nodes: List[ResourceStatus]
    pods: List[ResourceStatus]
    containers: List[ResourceStatus]
