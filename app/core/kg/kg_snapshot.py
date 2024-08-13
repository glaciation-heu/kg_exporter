from typing import List

from dataclasses import dataclass, field

from app.core.kg.resource_status_query import ResourceStatus


@dataclass
class KGSnapshot:
    nodes: List[ResourceStatus] = field(default_factory=list)
    pods: List[ResourceStatus] = field(default_factory=list)
    containers: List[ResourceStatus] = field(default_factory=list)
