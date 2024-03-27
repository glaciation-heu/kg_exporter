from typing import Any, Dict, List

import json
from io import FileIO
from unittest import TestCase

from app.k8s_transform.transformer_base import TransformerBase
from app.kg.id_base import IdBase
from app.kg.iri import IRI
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

    def load_json_list(self, name: str) -> List[Dict[str, Any]]:
        with FileIO(f"app/k8s_transform/__fixture__/{name}.json") as f:
            return json.load(f)  # type: ignore

    def get_jsonld_config(self) -> JsonLDConfiguration:
        contexts: Dict[IdBase, Dict[str, Any]] = {
            JsonLDConfiguration.DEFAULT_CONTEXT_IRI: {
                "gla": "http://glaciation-project.eu/model/",
                "cluster": "https://127.0.0.1:6443",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            }
        }
        return JsonLDConfiguration(
            contexts, {IRI(TransformerBase.GLACIATION_PREFIX, "Pod")}
        )
