from typing import Any, Dict, Tuple

import json
from io import FileIO

from app.kg.graph import Graph
from app.kg.id_base import IdBase
from app.kg.inmemory_graph import InMemoryGraph
from app.kg.iri import IRI
from app.serialize.jsonld_configuration import JsonLDConfiguration
from app.transform.k8s.upper_ontology_base import UpperOntologyBase


class TestTransformer(UpperOntologyBase):
    def __init__(self, graph: Graph):
        super().__init__(graph)


class TestGraphFixture:
    def simple_node(self) -> Tuple[Graph, str]:
        graph = InMemoryGraph()
        node1 = IRI("glc", "node1")
        cpu = IRI("glc", "cpu")
        measurement_id = IRI("glc", "measurement1")

        transformer = TestTransformer(graph)
        transformer.add_work_producing_resource(node1, "Node")
        transformer.add_work_producing_resource(cpu, "CPU")
        transformer.add_subresource(node1, cpu)
        transformer.add_measurement(
            measurement_id,
            "CPU.MAX",
            42.0,
            1700000000,
            UpperOntologyBase.UNIT_CPU_CORE_ID,
            UpperOntologyBase.PROPERTY_CPU_CAPACITY,
            UpperOntologyBase.MEASURING_RESOURCE_NODE_K8S_SPEC_ID,
        )

        serialized = self.load_json("simple_node")
        return graph, json.dumps(serialized)

    def get_jsonld_config(self) -> JsonLDConfiguration:
        contexts: Dict[IdBase, Dict[str, Any]] = {
            JsonLDConfiguration.DEFAULT_CONTEXT_IRI: self.get_test_context()
        }
        return JsonLDConfiguration(
            contexts,
            {
                UpperOntologyBase.WORK_PRODUCING_RESOURCE,
                UpperOntologyBase.NON_WORK_PRODUCING_RESOURCE,
                UpperOntologyBase.ASPECT,
                UpperOntologyBase.MEASUREMENT_PROPERTY,
                UpperOntologyBase.MEASURING_RESOURCE,
                UpperOntologyBase.MEASUREMENT_UNIT,
            },
        )

    def get_test_context(self) -> Dict[str, Any]:
        context = {
            "k8s": "http://glaciation-project.eu/model/k8s/",
            "glc": "https://glaciation-heu.github.io/models/reference_model.turtle",
            "cluster": "https://127.0.0.1:6443/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
        return context

    def load_json(self, name: str) -> Dict[str, Any]:
        with FileIO(f"app/core/__fixture__/{name}.jsonld") as f:
            return json.load(f)  # type: ignore
