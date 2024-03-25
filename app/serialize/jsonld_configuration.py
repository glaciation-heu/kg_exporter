from typing import Any, Dict, Set

from dataclasses import dataclass

from app.kg.id_base import IdBase
from app.kg.iri import IRI


@dataclass
class JsonLDConfiguration:
    DEFAULT_CONTEXT_IRI = IRI("__default__", "__default__")

    contexts: Dict[IdBase, Dict[str, Any]]
    aggregates: Set[IRI]
