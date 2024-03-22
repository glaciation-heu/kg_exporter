from typing import Any, Dict, Set

from dataclasses import dataclass


@dataclass
class JsonLDConfiguration:
    contexts: Dict[str, Dict[str, Any]]
    aggregates: Set[str]
