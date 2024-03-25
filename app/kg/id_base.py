from abc import abstractmethod


class IdBase:
    @abstractmethod
    def is_string_type(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def render(self) -> str:
        raise NotImplementedError
