from typing import Set, TypeAlias

from app.kg.iri import IRI
from app.kg.literal import Literal

LiteralSet: TypeAlias = Set[Literal]
RelationSet: TypeAlias = Set[IRI]
