from typing import Any, Dict

from dataclasses import dataclass
from enum import StrEnum


class Kind(StrEnum):
    POD = "Pod"
    NODE = "Node"


class EventType(StrEnum):
    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    DELETED = "DELETED"


@dataclass
class K8SEvent:
    event: EventType
    kind: Kind
    version: int
    resource: Dict[str, Any]
