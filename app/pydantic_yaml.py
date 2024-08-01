from typing import Type

from enum import StrEnum

from pydantic_settings import BaseSettings
from yaml import SafeDumper, representer, safe_dump, safe_load


def from_yaml(file_path: str, cls: Type[BaseSettings]) -> BaseSettings:
    SafeDumper.add_multi_representer(StrEnum, representer.SafeRepresenter.represent_str)
    with open(file_path, "r") as file:
        file_struct = safe_load(file)
        return cls.model_validate(file_struct)


def to_yaml(file_path: str, obj: BaseSettings) -> None:
    SafeDumper.add_multi_representer(StrEnum, representer.SafeRepresenter.represent_str)
    obj_dict = obj.model_dump()
    with open(file_path, "w") as file:
        safe_dump(obj_dict, file)
