from typing import Any


class IRI:
    prefix: str
    value: str

    def __init__(self, prefix: str, value: str):
        self.prefix = prefix
        self.value = value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, IRI):
            return NotImplemented
        if self is other:
            return True

        return self.prefix == other.prefix and self.value == other.value

    def __hash__(self) -> int:
        res = 7
        res ^= self.prefix.__hash__()
        res ^= self.value.__hash__()
        return res

    def render(self) -> str:
        result = f"{self.prefix}:{self.value}"
        return result
