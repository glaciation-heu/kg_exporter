from typing import Any, Optional

from app.kg.id_base import IdBase


class IRI(IdBase):
    prefix: str
    value: str

    def __init__(self, prefix: str, value: str):
        self.prefix = prefix
        self.value = value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, IRI):
            raise NotImplementedError
        if self is other:
            return True

        return self.prefix == other.prefix and self.value == other.value

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, IRI):
            if self.prefix.__gt__(other.prefix):
                return True
            if self.prefix.__eq__(other.prefix) and self.value.__gt__(other.value):
                return True
            return False
        else:
            raise NotImplementedError

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, IRI):
            try:
                return not self.__gt__(other) and not self.__eq__(other)
            except TypeError:
                raise NotImplementedError
        raise NotImplementedError

    def __le__(self, other: Any) -> bool:
        r = self.__lt__(other)
        if r:
            return True
        try:
            return self.__eq__(other)
        except TypeError:
            raise NotImplementedError

    def __ge__(self, other: Any) -> bool:
        r = self.__gt__(other)
        if r:
            return True
        try:
            return self.__eq__(other)
        except TypeError:
            raise NotImplementedError

    def __hash__(self) -> int:
        res = 7
        res ^= self.prefix.__hash__()
        res ^= self.value.__hash__()
        return res

    def dot(self, token: str) -> "IRI":
        return IRI(self.prefix, f"{self.value}.{token}")

    def render(self) -> str:
        result = f"{self.prefix}:{self.value}"
        return result

    def is_string_type(self) -> bool:
        return False

    def get_prefix(self) -> Optional[str]:
        return self.prefix

    def get_value(self) -> str:
        return self.value
