from typing import List, Optional

from app.kg.graph import Graph
from app.kg.iri import IRI
from app.kg.literal import Literal


class UpperOntologyBase:
    GLACIATION_PREFIX = "glc"
    HAS_ID = IRI(GLACIATION_PREFIX, "hasID")
    HAS_DESCRIPTION = IRI(GLACIATION_PREFIX, "hasDescription")
    HAS_SUBRESOURCE = IRI(GLACIATION_PREFIX, "hasSubResource")
    HAS_MEASUREMENT = IRI(GLACIATION_PREFIX, "hasMeasurement")
    PRODUCES = IRI(GLACIATION_PREFIX, "produces")
    MAKES = IRI(GLACIATION_PREFIX, "makes")

    # Measuring Resources
    MEASURING_RESOURCE_KEPLER_ID = IRI(GLACIATION_PREFIX, "Kepler")
    MEASURING_RESOURCE_NODE_EXPORTER_ID = IRI(GLACIATION_PREFIX, "NodeExporter")
    MEASURING_RESOURCE_NODE_K8S_SPEC_ID = IRI(
        GLACIATION_PREFIX, "ResourceSpecification"
    )
    MEASURING_RESOURCE_NODE_CADVISOR_ID = IRI(GLACIATION_PREFIX, "cAdvisor")
    MEASURING_RESOURCE_NODE_ENERGY_BENCHMARK = IRI(GLACIATION_PREFIX, "EnergyBenchmark")

    # Units
    UNIT_CPU_CORE_ID = IRI(GLACIATION_PREFIX, "Core")
    UNIT_GB_ID = IRI(GLACIATION_PREFIX, "GB")
    UNIT_BYTES_ID = IRI(GLACIATION_PREFIX, "Bytes")
    UNIT_MB_ID = IRI(GLACIATION_PREFIX, "MB")
    UNIT_MILLIWATT_ID = IRI(GLACIATION_PREFIX, "Milliwatt")

    # Aspects
    ASPECT_POWER_ID = IRI(GLACIATION_PREFIX, "Power")
    ASPECT_PERFORMANCE_ID = IRI(GLACIATION_PREFIX, "Performance")

    # Properties
    PROPERTY_CPU_CAPACITY = IRI(GLACIATION_PREFIX, "CPU.Capacity")
    PROPERTY_CPU_AVAILABLE = IRI(GLACIATION_PREFIX, "CPU.Available")
    PROPERTY_CPU_USAGE = IRI(GLACIATION_PREFIX, "CPU.Usage")
    PROPERTY_GPU_CAPACITY = IRI(GLACIATION_PREFIX, "GPU.Capacity")
    PROPERTY_GPU_AVAILABLE = IRI(GLACIATION_PREFIX, "GPU.Available")
    PROPERTY_GPU_USAGE = IRI(GLACIATION_PREFIX, "GPU.Usage")
    PROPERTY_RAM_CAPACITY = IRI(GLACIATION_PREFIX, "RAM.Capacity")
    PROPERTY_RAM_AVAILABLE = IRI(GLACIATION_PREFIX, "RAM.Available")
    PROPERTY_RAM_USAGE = IRI(GLACIATION_PREFIX, "RAM.Usage")
    PROPERTY_STORAGE_CAPACITY = IRI(GLACIATION_PREFIX, "Storage.Capacity")
    PROPERTY_STORAGE_AVAILABLE = IRI(GLACIATION_PREFIX, "Storage.Available")
    PROPERTY_STORAGE_USAGE = IRI(GLACIATION_PREFIX, "Storage.Usage")
    PROPERTY_NETWORK_CAPACITY = IRI(GLACIATION_PREFIX, "Network.Capacity")
    PROPERTY_NETWORK_AVAILABLE = IRI(GLACIATION_PREFIX, "Network.Available")
    PROPERTY_NETWORK_USAGE = IRI(GLACIATION_PREFIX, "Network.Usage")
    PROPERTY_ENERGY_INDEX = IRI(GLACIATION_PREFIX, "Energy.Index")
    PROPERTY_ENERGY_AVAILABLE = IRI(GLACIATION_PREFIX, "Energy.Available")
    PROPERTY_ENERGY_USAGE = IRI(GLACIATION_PREFIX, "Energy.Usage")

    units: List[IRI]
    aspects: List[IRI]
    properties: List[IRI]

    sink: Graph

    def __init__(self, sink: Graph):
        self.sink = sink

        self.units = [
            self.UNIT_CPU_CORE_ID,
            self.UNIT_GB_ID,
            self.UNIT_BYTES_ID,
            self.UNIT_MB_ID,
            self.UNIT_MILLIWATT_ID,
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

    def add_aspect(self, identifier: IRI, description: Optional[str]) -> None:
        self.add_common_info(identifier, "Aspect", description)

    def add_measurement_property(
        self, identifier: IRI, description: Optional[str]
    ) -> None:
        self.add_common_info(identifier, "MeasurementProperty", description)

    def add_status(
        self, identifier: IRI, status: str, start_time: str, end_time: Optional[str]
    ) -> None:
        self.add_common_info(identifier, "Status", status)
        self.sink.add_property(
            identifier,
            IRI(self.GLACIATION_PREFIX, "startTime"),
            Literal(start_time, "str"),
        )
        if end_time:
            self.sink.add_property(
                identifier,
                IRI(self.GLACIATION_PREFIX, "endTime"),
                Literal(end_time, "str"),
            )

    def add_measurement(
        self,
        identifier: IRI,
        description: str,
        value: float,
        timestamp: int,
        unit: IRI,
        related_to_property: IRI,
        measuring_resource: IRI,
    ) -> None:
        self.add_common_info(identifier, "Measurement", description)
        self.sink.add_property(
            identifier,
            IRI(self.GLACIATION_PREFIX, "hasValue"),
            Literal(value, "int"),
        )
        self.sink.add_property(
            identifier,
            IRI(self.GLACIATION_PREFIX, "hasTimestamp"),
            Literal(timestamp, "int"),
        )
        self.sink.add_relation(
            identifier,
            IRI(self.GLACIATION_PREFIX, "relatesToMeasurementProperty"),
            related_to_property,
        )
        self.sink.add_relation(
            identifier, IRI(self.GLACIATION_PREFIX, "measuredIn"), unit
        )
        self.sink.add_relation(
            measuring_resource, IRI(self.GLACIATION_PREFIX, "makes"), identifier
        )

    def add_measuring_resource(self, identifier: IRI, description: str) -> None:
        self.add_common_info(identifier, "MeasuringResource", description)

    def add_unit(self, identifier: IRI, description: Optional[str]) -> None:
        self.add_common_info(identifier, "MeasurementUnit", description)

    def add_constraint(
        self,
        identifier: str,
        description: str,
        is_soft_constraint: bool,
        value: int,
        unit: IRI,
        aspect: IRI,
    ) -> None:
        constraint_id = IRI(self.GLACIATION_PREFIX, identifier)
        if is_soft_constraint:
            self.add_common_info(constraint_id, "SoftConstraint", description)
        else:
            self.add_common_info(constraint_id, "HardConstraint", description)
        self.sink.add_property(
            constraint_id,
            IRI(self.GLACIATION_PREFIX, "maxValue"),
            Literal(value, "int"),
        )
        self.sink.add_relation(
            constraint_id, IRI(self.GLACIATION_PREFIX, "measuredIn"), unit
        )
        self.sink.add_relation(
            constraint_id, IRI(self.GLACIATION_PREFIX, "hasAspect"), aspect
        )

    def add_assigned_task(self, identifier: str, description: str) -> IRI:
        task_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(task_id, "AssignedTask", description)
        return task_id

    def add_submitted_task(self, identifier: str, description: str) -> IRI:
        task_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(task_id, "SubmittedTask", description)
        return task_id

    def add_non_work_producing_resource(
        self, identifier: IRI, description: Optional[str]
    ) -> None:
        self.add_common_info(identifier, "NonWorkProducingResource", description)

    def add_work_producing_resource(
        self, identifier: IRI, description: Optional[str]
    ) -> None:
        self.add_common_info(identifier, "WorkProducingResource", description)

    def add_common_info(
        self, entity_id: IRI, entity_type: str, description: Optional[str]
    ) -> None:
        self.sink.add_meta_property(
            entity_id, Graph.RDF_TYPE_IRI, IRI(self.GLACIATION_PREFIX, entity_type)
        )
        self.sink.add_relation(entity_id, self.HAS_ID, entity_id)
        if description:
            self.sink.add_property(
                entity_id,
                self.HAS_DESCRIPTION,
                Literal(description, Literal.TYPE_STRING),
            )

    def add_common_entities(self) -> None:
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

        for unit in self.units:
            self.add_unit(unit, None)

        for aspect in self.aspects:
            self.add_aspect(aspect, None)

        for property in self.properties:
            self.add_measurement_property(property, None)
