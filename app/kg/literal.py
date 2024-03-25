from typing import Any

from app.kg.graph import PropertyValue


class Literal:
    value: PropertyValue
    _type: str

    def __init__(self, value: PropertyValue, _type: str):
        self.value = value
        self._type = _type

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Literal):
            return NotImplemented

        if self is other:
            return True

        return self.value == other.value and self._type == other._type

    def __hash__(self) -> int:
        res = 7
        res ^= self._type.__hash__()
        res ^= hash(self.value)
        return res

    def render(self) -> str:
        return f"{self.value}"
