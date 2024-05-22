from typing import List

from app.k8s_transform.upper_ontology_base import UpperOntologyBase
from app.kg.graph import Graph
from app.kg.iri import IRI


class GlaciationCommonEntities(UpperOntologyBase):
    MEASURING_RESOURCE_KEPLER_ID = IRI(UpperOntologyBase.GLACIATION_PREFIX, "Kepler")
    MEASURING_RESOURCE_NODE_EXPORTER_ID = IRI(
        UpperOntologyBase.GLACIATION_PREFIX, "NodeExporter"
    )
    MEASURING_RESOURCE_NODE_K8S_SPEC_ID = IRI(
        UpperOntologyBase.GLACIATION_PREFIX, "ResourceSpecification"
    )
    MEASURING_RESOURCE_NODE_CADVISOR_ID = IRI(
        UpperOntologyBase.GLACIATION_PREFIX, "cAdvisor"
    )
    MEASURING_RESOURCE_NODE_ENERGY_BENCHMARK = IRI(
        UpperOntologyBase.GLACIATION_PREFIX, "EnergyBenchmark"
    )

    UNIT_CPU_CORE_ID = IRI(UpperOntologyBase.GLACIATION_PREFIX, "Core")
    UNIT_CPU_GB_ID = IRI(UpperOntologyBase.GLACIATION_PREFIX, "GB")
    UNIT_CPU_MB_ID = IRI(UpperOntologyBase.GLACIATION_PREFIX, "MB")
    UNIT_CPU_MILLIWATT_ID = IRI(UpperOntologyBase.GLACIATION_PREFIX, "Milliwatt")

    ASPECT_POWER_ID = IRI(UpperOntologyBase.GLACIATION_PREFIX, "Power")
    ASPECT_PERFORMANCE_ID = IRI(UpperOntologyBase.GLACIATION_PREFIX, "Performance")

    PROPERTY_CPU_CAPACITY = IRI(UpperOntologyBase.GLACIATION_PREFIX, "CPU.Capacity")
    PROPERTY_CPU_AVAILABLE = IRI(UpperOntologyBase.GLACIATION_PREFIX, "CPU.Available")
    PROPERTY_CPU_USAGE = IRI(UpperOntologyBase.GLACIATION_PREFIX, "CPU.Usage")
    PROPERTY_GPU_CAPACITY = IRI(UpperOntologyBase.GLACIATION_PREFIX, "GPU.Capacity")
    PROPERTY_GPU_AVAILABLE = IRI(UpperOntologyBase.GLACIATION_PREFIX, "GPU.Available")
    PROPERTY_GPU_USAGE = IRI(UpperOntologyBase.GLACIATION_PREFIX, "GPU.Usage")
    PROPERTY_RAM_CAPACITY = IRI(UpperOntologyBase.GLACIATION_PREFIX, "RAM.Capacity")
    PROPERTY_RAM_AVAILABLE = IRI(UpperOntologyBase.GLACIATION_PREFIX, "RAM.Available")
    PROPERTY_RAM_USAGE = IRI(UpperOntologyBase.GLACIATION_PREFIX, "RAM.Usage")
    PROPERTY_STORAGE_CAPACITY = IRI(
        UpperOntologyBase.GLACIATION_PREFIX, "Storage.Capacity"
    )
    PROPERTY_STORAGE_AVAILABLE = IRI(
        UpperOntologyBase.GLACIATION_PREFIX, "Storage.Available"
    )
    PROPERTY_STORAGE_USAGE = IRI(UpperOntologyBase.GLACIATION_PREFIX, "Storage.Usage")
    PROPERTY_NETWORK_CAPACITY = IRI(
        UpperOntologyBase.GLACIATION_PREFIX, "Network.Capacity"
    )
    PROPERTY_NETWORK_AVAILABLE = IRI(
        UpperOntologyBase.GLACIATION_PREFIX, "Network.Available"
    )
    PROPERTY_NETWORK_USAGE = IRI(UpperOntologyBase.GLACIATION_PREFIX, "Network.Usage")
    PROPERTY_ENERGY_INDEX = IRI(UpperOntologyBase.GLACIATION_PREFIX, "Energy.Index")
    PROPERTY_ENERGY_AVAILABLE = IRI(
        UpperOntologyBase.GLACIATION_PREFIX, "Energy.Available"
    )
    PROPERTY_ENERGY_USAGE = IRI(UpperOntologyBase.GLACIATION_PREFIX, "Energy.Usage")

    units: List[IRI]
    aspects: List[IRI]
    properties: List[IRI]

    def __init__(self, sink: Graph):
        UpperOntologyBase.__init__(self, sink)
        self.units = [
            self.UNIT_CPU_CORE_ID,
            self.UNIT_CPU_GB_ID,
            self.UNIT_CPU_MB_ID,
            self.UNIT_CPU_MILLIWATT_ID,
        ]
        self.aspects = [self.ASPECT_POWER_ID, self.ASPECT_PERFORMANCE_ID]
        self.properties = [
            self.PROPERTY_CPU_CAPACITY,
            self.PROPERTY_CPU_AVAILABLE,
            self.PROPERTY_CPU_USAGE,
            self.PROPERTY_GPU_CAPACITY,
            self.PROPERTY_GPU_AVAILABLE,
            self.PROPERTY_GPU_USAGE,
            self.PROPERTY_RAM_CAPACITY,
            self.PROPERTY_RAM_AVAILABLE,
            self.PROPERTY_RAM_USAGE,
            self.PROPERTY_STORAGE_CAPACITY,
            self.PROPERTY_STORAGE_AVAILABLE,
            self.PROPERTY_STORAGE_USAGE,
            self.PROPERTY_NETWORK_CAPACITY,
            self.PROPERTY_NETWORK_AVAILABLE,
            self.PROPERTY_NETWORK_USAGE,
            self.PROPERTY_ENERGY_INDEX,
            self.PROPERTY_ENERGY_AVAILABLE,
            self.PROPERTY_ENERGY_USAGE,
        ]

    def transform(self) -> None:
        self.add_measuring_resource(
            self.MEASURING_RESOURCE_KEPLER_ID,
            "Kepler metrics https://sustainable-computing.io/",
        )
        self.add_measuring_resource(
            self.MEASURING_RESOURCE_NODE_EXPORTER_ID, "NodeExporter"
        )
        self.add_measuring_resource(
            self.MEASURING_RESOURCE_NODE_K8S_SPEC_ID, "ResourceSpecification"
        )
        self.add_measuring_resource(
            self.MEASURING_RESOURCE_NODE_CADVISOR_ID,
            """cAdvisor metrics https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md""",  # noqa: E501
        )
        self.add_measuring_resource(
            self.MEASURING_RESOURCE_NODE_ENERGY_BENCHMARK, "EnergyBenchmark"
        )

        for aspect in self.aspects:
            self.add_aspect(aspect, None)

        for property in self.properties:
            self.add_measurement_property(property, None)
