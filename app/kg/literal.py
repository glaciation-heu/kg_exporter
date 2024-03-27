from typing import Any, Optional, TypeAlias

from app.kg.id_base import IdBase

PropertyValue: TypeAlias = str | int | bool | float


class Literal(IdBase):
    TYPE_STRING = "str"
    TYPE_INT = "int"
    TYPE_FLOAT = "float"
    TYPE_BOOL = "bool"

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

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, Literal):
            if self._type.__eq__(other._type):
                return self.value.__gt__(other.value)  # type: ignore[operator]
            else:
                # TODO int and float are still comparable
                return NotImplemented
        else:
            return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Literal):
            try:
                return not self.__gt__(other) and not self.__eq__(other)
            except TypeError:
                return NotImplemented
        return NotImplemented

    def __le__(self, other: Any) -> bool:
        r = self.__lt__(other)
        if r:
            return True
        try:
            return self.__eq__(other)
        except TypeError:
            return NotImplemented

    def __ge__(self, other: Any) -> bool:
        r = self.__gt__(other)
        if r:
            return True
        try:
            return self.__eq__(other)
        except TypeError:
            return NotImplemented

    def __hash__(self) -> int:
        res = 7
        res ^= self._type.__hash__()
        res ^= hash(self.value)
        return res

    def render(self) -> str:
        return f"{self.value}"

    def is_string_type(self) -> bool:
        return self._type == self.TYPE_STRING

    def get_prefix(self) -> Optional[str]:
        return None
