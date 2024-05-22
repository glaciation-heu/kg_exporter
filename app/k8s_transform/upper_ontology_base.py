from typing import Optional

from app.kg.graph import Graph
from app.kg.iri import IRI
from app.kg.literal import Literal


class UpperOntologyBase:
    GLACIATION_PREFIX = "glc"
    HAS_ID = IRI(GLACIATION_PREFIX, "hasID")
    HAS_DESCRIPTION = IRI(GLACIATION_PREFIX, "hasDescription")
    HAS_SUBRESOURCE = IRI(GLACIATION_PREFIX, "hasSubResource")
    PRODUCES = IRI(GLACIATION_PREFIX, "produces")
    MAKES = IRI(GLACIATION_PREFIX, "makes")
    sink: Graph

    def __init__(self, sink: Graph):
        self.sink = sink

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
            Literal(value, "str"),
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

    def add_unit(self, identifier: IRI, description: str) -> None:
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
        self.sink.add_relation(entity_id, UpperOntologyBase.HAS_ID, entity_id)
        if description:
            self.sink.add_property(
                entity_id,
                UpperOntologyBase.HAS_DESCRIPTION,
                Literal(description, Literal.TYPE_STRING),
            )
