from typing import Type

from pydantic_settings import BaseSettings
from yaml import safe_dump, safe_load


def from_yaml(file_path: str, cls: Type[BaseSettings]) -> BaseSettings:
    with open(file_path, "r") as file:
        file_struct = safe_load(file)
        return cls.model_validate(file_struct)


def to_yaml(file_path: str, obj: BaseSettings) -> None:
    obj_dict = obj.model_dump()
    with open(file_path, "w") as file:
        safe_dump(obj_dict, file)
