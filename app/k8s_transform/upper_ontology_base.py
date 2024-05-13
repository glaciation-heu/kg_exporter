from typing import Optional

from app.kg.graph import Graph
from app.kg.iri import IRI
from app.kg.literal import Literal


class UpperOntologyBase:
    GLACIATION_PREFIX = "glc"
    HAS_ID = IRI(GLACIATION_PREFIX, "hasID")
    HAS_DESCRIPTION = IRI(GLACIATION_PREFIX, "hasID")
    sink: Graph

    def __init__(self, sink: Graph):
        self.sink = sink

    def add_aspect(self, identifier: str, description: str) -> None:
        aspect_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(aspect_id, "Aspect", description)

    def add_measuring_property(self, identifier: str, description: str) -> None:
        property_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(property_id, "MeasurementProperty", description)

    def add_status(
        self, identifier: str, status: str, start_time: int, end_time: Optional[int]
    ) -> None:
        status_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(status_id, "Status", status)

    def add_measurement(
        self,
        identifier: str,
        description: str,
        value: float,
        timestamp: int,
        unit: IRI,
        related_to_property: IRI,
    ) -> None:
        measurement_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(measurement_id, "Measurement", description)

    def add_measuring_resource(self, identifier: str, description: str) -> None:
        resource_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(resource_id, "MeasuringResource", description)

    def add_unit(self, identifier: str, description: str) -> None:
        unit_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(unit_id, "MeasurementUnit", description)

    def add_soft_constraint(
        self, identifier: str, description: str, value: int, unit: IRI
    ) -> None:
        constraint_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(constraint_id, "SoftConstraint", description)

    def add_assigned_task(self, identifier: str, description: str) -> None:
        unit_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(unit_id, "AssignedTask", description)

    def add_submitted_task(self, identifier: str, description: str) -> None:
        unit_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(unit_id, "SubmittedTask", description)

    def add_non_work_producing_resource(
        self, identifier: str, description: str
    ) -> None:
        unit_id = IRI(self.GLACIATION_PREFIX, identifier)
        self.add_common_info(unit_id, "NonWorkProducingResource", description)

    def add_common_info(
        self, entity_id: IRI, entity_type: str, description: str
    ) -> None:
        self.sink.add_meta_property(
            entity_id, Graph.RDF_TYPE_IRI, IRI(self.GLACIATION_PREFIX, entity_type)
        )
        self.sink.add_property(
            entity_id,
            UpperOntologyBase.HAS_ID,
            Literal(entity_id.render(), Literal.TYPE_STRING),
        )
        self.sink.add_property(
            entity_id,
            UpperOntologyBase.HAS_DESCRIPTION,
            Literal(description, Literal.TYPE_STRING),
        )
