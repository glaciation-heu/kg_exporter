from typing import Any, Dict

import json
from io import FileIO
from unittest import TestCase


class TransformBaseTest(TestCase):
    def load_turtle(self, name: str) -> str:
        with FileIO(f"app/rdf_transform/__fixture__/{name}.turtle") as f:
            return f.readall().decode("utf-8")

    def load_json(self, name: str) -> Dict[str, Any]:
        with FileIO(f"app/rdf_transform/__fixture__/{name}.json") as f:
            return json.load(f)  # type: ignore
