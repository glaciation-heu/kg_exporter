from typing import Dict, List, Optional

from dataclasses import dataclass

from app.kg.graph import Graph
from app.kg.iri import IRI
from app.kg.literal import Literal


@dataclass
class Aggregation:
    function: str
    starting_interval: int
    ending_interval: int


class UpperOntologyBase:
    GLACIATION_PREFIX = "glc"
    # Entities

    ASSIGNED_TASK = IRI(GLACIATION_PREFIX, "AssignedTask")
    SUBMITTED_TASK = IRI(GLACIATION_PREFIX, "SubmittedTask")
    WORK_PRODUCING_RESOURCE = IRI(GLACIATION_PREFIX, "WorkProducingResource")
    NON_WORK_PRODUCING_RESOURCE = IRI(GLACIATION_PREFIX, "NonWorkProducingResource")
    ASPECT = IRI(GLACIATION_PREFIX, "Aspect")
    MEASUREMENT_PROPERTY = IRI(GLACIATION_PREFIX, "MeasurementProperty")
    STATUS = IRI(GLACIATION_PREFIX, "Status")
    MEASUREMENT = IRI(GLACIATION_PREFIX, "Measurement")
    AGGREGATED_MEASUREMENT = IRI(GLACIATION_PREFIX, "AggregatedMeasurement")
    MEASURING_RESOURCE = IRI(GLACIATION_PREFIX, "MeasuringResource")
    MEASUREMENT_UNIT = IRI(GLACIATION_PREFIX, "MeasurementUnit")
    SOFT_CONSTRAINT = IRI(GLACIATION_PREFIX, "SoftConstraint")
    HARD_CONSTRAINT = IRI(GLACIATION_PREFIX, "HardConstraint")
    SCHEDULER = IRI(GLACIATION_PREFIX, "Scheduler")

    # Relations
    HAS_ID = IRI(GLACIATION_PREFIX, "hasID")
    HAS_DESCRIPTION = IRI(GLACIATION_PREFIX, "hasDescription")
    HAS_SUBRESOURCE = IRI(GLACIATION_PREFIX, "hasSubResource")
    HAS_SUBTASK = IRI(GLACIATION_PREFIX, "hasSubTask")
    HAS_MEASUREMENT = IRI(GLACIATION_PREFIX, "hasMeasurement")
    HAS_STATUS = IRI(GLACIATION_PREFIX, "hasStatus")
    HAS_ASPECT = IRI(GLACIATION_PREFIX, "hasAspect")
    HAS_CONSTRAINT = IRI(GLACIATION_PREFIX, "hasConstraint")
    PRODUCES = IRI(GLACIATION_PREFIX, "produces")
    CONSUMES = IRI(GLACIATION_PREFIX, "consumes")
    ASSIGNS = IRI(GLACIATION_PREFIX, "assigns")
    MAKES = IRI(GLACIATION_PREFIX, "makes")
    MANAGES = IRI(GLACIATION_PREFIX, "manages")
    MEASURED_IN = IRI(GLACIATION_PREFIX, "measuredIn")
    START_TIME = IRI(GLACIATION_PREFIX, "startTime")
    END_TIME = IRI(GLACIATION_PREFIX, "endTime")
    HAS_VALUE = IRI(GLACIATION_PREFIX, "hasValue")
    HAS_TIMESTAMP = IRI(GLACIATION_PREFIX, "hasTimestamp")
    RELATES_TO_MEASUREMENT_PROPERTY = IRI(
        GLACIATION_PREFIX, "relatesToMeasurementProperty"
    )
    TIMESTEP_RESOLUTION = IRI(GLACIATION_PREFIX, "timestepResolution")
    HAS_AGGREGATED_FUNCTION = IRI(GLACIATION_PREFIX, "hasAggregatedFunction")
    STARTING_INTERVAL = IRI(GLACIATION_PREFIX, "startingInterval")
    ENDING_INTERVAL = IRI(GLACIATION_PREFIX, "endingInterval")

    # Measuring Resources
    MEASURING_RESOURCE_KEPLER_ID = IRI(GLACIATION_PREFIX, "Kepler")
    MEASURING_RESOURCE_NODE_EXPORTER_ID = IRI(GLACIATION_PREFIX, "NodeExporter")
    MEASURING_RESOURCE_NODE_K8S_SPEC_ID = IRI(
        GLACIATION_PREFIX, "ResourceSpecification"
    )
    MEASURING_RESOURCE_NODE_CADVISOR_ID = IRI(GLACIATION_PREFIX, "cAdvisor")
    MEASURING_RESOURCE_NODE_ENERGY_BENCHMARK = IRI(GLACIATION_PREFIX, "EnergyBenchmark")

    MEASURING_RESOURCE_DESCRIPTIONS: Dict[IRI, str] = {
        MEASURING_RESOURCE_KEPLER_ID: "Kepler metrics https://sustainable-computing.io/",
        MEASURING_RESOURCE_NODE_EXPORTER_ID: "NodeExporter",
        MEASURING_RESOURCE_NODE_K8S_SPEC_ID: "ResourceSpecification",
        MEASURING_RESOURCE_NODE_CADVISOR_ID: "cAdvisor metrics https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md",  # noqa: E501
        MEASURING_RESOURCE_NODE_ENERGY_BENCHMARK: "EnergyBenchmark",
    }

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
    measuring_resources: List[IRI]

    sink: Graph

    def __init__(self, sink: Graph):
        self.sink = sink
        self.measuring_resources = [
            self.MEASURING_RESOURCE_KEPLER_ID,
            self.MEASURING_RESOURCE_NODE_EXPORTER_ID,
            self.MEASURING_RESOURCE_NODE_K8S_SPEC_ID,
            self.MEASURING_RESOURCE_NODE_CADVISOR_ID,
            self.MEASURING_RESOURCE_NODE_ENERGY_BENCHMARK,
        ]
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
        self.add_common_info(identifier, self.ASPECT, description)

    def add_measurement_property(
        self, identifier: IRI, description: Optional[str]
    ) -> None:
        self.add_common_info(identifier, self.MEASUREMENT_PROPERTY, description)

    def add_status(
        self,
        identifier: IRI,
        status: str,
        start_time: Optional[str],
        end_time: Optional[str],
    ) -> None:
        self.add_common_info(identifier, self.STATUS, status)
        if start_time:
            self.sink.add_property(
                identifier,
                self.START_TIME,
                Literal(start_time, Literal.TYPE_DATE, "%Y-%m-%dT%H:%M:%S%z"),
            )
        if end_time:
            self.sink.add_property(
                identifier,
                self.END_TIME,
                Literal(end_time, Literal.TYPE_DATE, "%Y-%m-%dT%H:%M:%S%z"),
            )

    def add_measurement(
        self,
        identifier: IRI,
        description: str,
        value: float,
        timestamp: int,
        aggregation: Optional[Aggregation],
        unit: IRI,
        related_to_property: IRI,
        measuring_resource: IRI,
    ) -> None:
        if aggregation:
            self.add_common_info(identifier, self.AGGREGATED_MEASUREMENT, description)
            self.add_aggregation_properties(identifier, aggregation)
        else:
            self.add_common_info(identifier, self.MEASUREMENT, description)

        if not self.sink.has_node(unit):
            self.add_unit(unit, None)

        if not self.sink.has_node(related_to_property):
            self.add_measurement_property(related_to_property, None)

        if not self.sink.has_node(measuring_resource):
            self.add_measuring_resource(measuring_resource)

        self.sink.add_property(
            identifier,
            self.HAS_VALUE,
            Literal(value, Literal.TYPE_FLOAT),
        )
        self.sink.add_property(
            identifier,
            self.HAS_TIMESTAMP,
            Literal(timestamp, Literal.TYPE_INT),
        )
        self.sink.add_relation(
            identifier,
            self.RELATES_TO_MEASUREMENT_PROPERTY,
            related_to_property,
        )
        self.sink.add_relation(identifier, self.MEASURED_IN, unit)
        self.sink.add_relation(measuring_resource, self.MAKES, identifier)

    def add_unit(self, identifier: IRI, description: Optional[str]) -> None:
        self.add_common_info(identifier, self.MEASUREMENT_UNIT, description)

    def add_constraint(
        self,
        identifier: IRI,
        description: str,
        is_soft_constraint: bool,
        value: float,
        unit: IRI,
        aspect: IRI,
    ) -> None:
        if not self.sink.has_node(unit):
            self.add_unit(unit, None)

        if not self.sink.has_node(aspect):
            self.add_aspect(aspect, None)

        if is_soft_constraint:
            self.add_common_info(identifier, self.SOFT_CONSTRAINT, description)
        else:
            self.add_common_info(identifier, self.HARD_CONSTRAINT, description)
        self.sink.add_property(
            identifier,
            IRI(self.GLACIATION_PREFIX, "maxValue"),
            Literal(value, Literal.TYPE_FLOAT),
        )
        self.sink.add_relation(identifier, self.MEASURED_IN, unit)
        self.sink.add_relation(identifier, self.HAS_ASPECT, aspect)

    def add_assigned_task(self, identifier: IRI, description: Optional[str]) -> None:
        self.add_common_info(identifier, self.ASSIGNED_TASK, description)

    def add_submitted_task(self, identifier: IRI, description: Optional[str]) -> None:
        self.add_common_info(identifier, self.SUBMITTED_TASK, description)

    def add_non_work_producing_resource(
        self, identifier: IRI, description: Optional[str]
    ) -> None:
        self.add_common_info(identifier, self.NON_WORK_PRODUCING_RESOURCE, description)

    def add_scheduler(self, identifier: IRI, description: Optional[str]) -> None:
        self.add_common_info(identifier, self.SCHEDULER, description)

    def add_work_producing_resource(
        self, identifier: IRI, description: Optional[str]
    ) -> None:
        self.add_common_info(identifier, self.WORK_PRODUCING_RESOURCE, description)

    def add_subresource(self, identifier: IRI, subresource: IRI) -> None:
        self.sink.add_relation(identifier, self.HAS_SUBRESOURCE, subresource)

    def add_common_info(
        self, entity_id: IRI, entity_type: IRI, description: Optional[str]
    ) -> None:
        if self.sink.has_node(entity_id):
            return
        self.sink.add_meta_property(entity_id, Graph.RDF_TYPE_IRI, entity_type)
        self.sink.add_relation(entity_id, self.HAS_ID, entity_id)
        if description:
            self.sink.add_property(
                entity_id,
                self.HAS_DESCRIPTION,
                Literal(description, Literal.TYPE_STRING),
            )

    def add_common_entities(self) -> None:
        for measuring_resource in self.measuring_resources:
            self.add_measuring_resource(measuring_resource)

        for unit in self.units:
            self.add_unit(unit, None)

        for aspect in self.aspects:
            self.add_aspect(aspect, None)

        for property in self.properties:
            self.add_measurement_property(property, None)

    def add_measuring_resource(self, measuring_resource_id: IRI) -> None:
        description = self.MEASURING_RESOURCE_DESCRIPTIONS.get(measuring_resource_id)
        self.add_common_info(
            measuring_resource_id, self.MEASURING_RESOURCE, description
        )

    def add_aggregation_properties(
        self, identifier: IRI, aggregation: Aggregation
    ) -> None:
        self.sink.add_property(
            identifier,
            self.HAS_AGGREGATED_FUNCTION,
            Literal(aggregation.function, Literal.TYPE_STRING),
        )
        self.sink.add_property(
            identifier,
            self.STARTING_INTERVAL,
            Literal(aggregation.starting_interval, Literal.TYPE_INT),
        )
        self.sink.add_property(
            identifier,
            self.ENDING_INTERVAL,
            Literal(aggregation.ending_interval, Literal.TYPE_INT),
        )
