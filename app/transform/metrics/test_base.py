from typing import Any, Dict, List

import json
from io import FileIO
from unittest import TestCase

from app.kg.id_base import IdBase
from app.kg.iri import IRI
from app.serialize.jsonld_configuration import JsonLDConfiguration
from app.transform.k8s.upper_ontology_base import UpperOntologyBase


class MetricTransformTestBase(TestCase):
    BASE_PATH = "app/transform/metrics/__fixture__/"

    def load_turtle(self, name: str) -> str:
        with FileIO(f"{self.BASE_PATH}/{name}.turtle") as f:
            return f.readall().decode("utf-8")

    def load_jsonld(self, name: str) -> str:
        with FileIO(f"{self.BASE_PATH}/{name}.jsonld") as f:
            return json.load(f)  # type: ignore

    def load_json(self, name: str) -> Dict[str, Any]:
        with FileIO(f"{self.BASE_PATH}/{name}.json") as f:
            return json.load(f)  # type: ignore

    def load_json_list(self, name: str) -> List[Dict[str, Any]]:
        with FileIO(f"{self.BASE_PATH}/{name}.json") as f:
            return json.load(f)  # type: ignore

    def get_jsonld_config(self) -> JsonLDConfiguration:
        contexts: Dict[IdBase, Dict[str, Any]] = {
            JsonLDConfiguration.DEFAULT_CONTEXT_IRI: {
                "k8s": "http://glaciation-project.eu/model/k8s/",
                "glc": "https://glaciation-heu.github.io/models/reference_model.turtle",
                "cluster": "https://127.0.0.1:6443/",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            }
        }
        return JsonLDConfiguration(
            contexts,
            {
                IRI(UpperOntologyBase.GLACIATION_PREFIX, "WorkProducingResource"),
                IRI(UpperOntologyBase.GLACIATION_PREFIX, "Aspect"),
                IRI(UpperOntologyBase.GLACIATION_PREFIX, "MeasurementProperty"),
                IRI(UpperOntologyBase.GLACIATION_PREFIX, "MeasuringResource"),
                IRI(UpperOntologyBase.GLACIATION_PREFIX, "MeasurementUnit"),
            },
        )
