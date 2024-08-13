from typing import Dict, Generic, List, TypeVar

from app.kg.id_base import IdBase

T = TypeVar("T")


class KGQuery(Generic[T]):
    def get_query(self) -> str:
        raise NotImplementedError

    def parse_results(self, result: List[Dict[str, IdBase]]) -> T:
        raise NotImplementedError
