from typing import Any, Dict

import json
from io import FileIO
from unittest import TestCase

from app.serialize.jsonld_configuration import JsonLDConfiguration


class TransformBaseTest(TestCase):
    def load_turtle(self, name: str) -> str:
        with FileIO(f"app/k8s_transform/__fixture__/{name}.turtle") as f:
            return f.readall().decode("utf-8")

    def load_jsonld(self, name: str) -> str:
        with FileIO(f"app/k8s_transform/__fixture__/{name}.jsonld") as f:
            return json.load(f)  # type: ignore

    def load_json(self, name: str) -> Dict[str, Any]:
        with FileIO(f"app/k8s_transform/__fixture__/{name}.json") as f:
            return json.load(f)  # type: ignore

    def get_jsonld_config(self) -> JsonLDConfiguration:
        contexts: Dict[str, Dict[str, str]] = dict()
        return JsonLDConfiguration(contexts, {"gla:Pod"})
