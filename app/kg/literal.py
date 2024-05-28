from typing import Any, Optional, Set, TypeAlias

from datetime import datetime

from app.kg.id_base import IdBase

PropertyValue: TypeAlias = str | int | bool | float


class Literal(IdBase):
    TYPE_STRING = "str"
    TYPE_INT = "int"
    TYPE_FLOAT = "float"
    TYPE_BOOL = "bool"
    TYPE_DATE = "date"

    LITERAL_TYPES: Set[str] = {TYPE_STRING, TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_DATE}

    value: PropertyValue
    _type: str
    format: Optional[str]

    def __init__(self, value: PropertyValue, _type: str, format: Optional[str] = None):
        if _type not in Literal.LITERAL_TYPES:
            raise Exception(
                f"Unknown literal type '{_type}' (literal value '{value}'). Expected one of {Literal.LITERAL_TYPES}."  # noqa: E501
            )
        if _type == Literal.TYPE_DATE:
            if not format:
                raise Exception(
                    f"Format is expected for the type '{Literal.TYPE_DATE}'."
                )
            if not isinstance(value, str):
                raise Exception(
                    f"Expected value for date type is 'str'. Actual '{type(value)}', value is '{value}'."  # noqa: E501
                )
            try:
                datetime.strptime(value, format)
            except Exception as e:
                raise Exception(
                    f"Unable parse datetime '{value}' according to format '{format}'. Error: {str(e)}"  # noqa: E501
                )
        self.value = value
        self._type = _type
        self.format = format

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Literal):
            return NotImplemented

        if self is other:
            return True

        return (
            self.value == other.value
            and self._type == other._type
            and self.format == other.format
        )

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, Literal):
            if self._type.__eq__(other._type) and self._type == Literal.TYPE_DATE:
                self_iso_date = datetime.strptime(self.value, self.format)  # type: ignore
                other_iso_date = datetime.strptime(other.value, other.format)  # type: ignore
                return self_iso_date.__gt__(other_iso_date)
            elif self._type.__eq__(other._type):
                return self.value.__gt__(other.value)  # type: ignore[operator]
            else:
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
        res ^= hash(self.format)
        return res

    def render(self) -> str:
        return f"{self.value}"

    def is_string_type(self) -> bool:
        return self._type == self.TYPE_STRING

    def is_date_type(self) -> bool:
        return self._type == self.TYPE_DATE

    def get_prefix(self) -> Optional[str]:
        return None

    def get_format(self) -> Optional[str]:
        return self.format
