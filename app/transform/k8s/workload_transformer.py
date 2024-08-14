from typing import Any, Dict, List, Optional

from app.kg.graph import Graph
from app.kg.iri import IRI
from app.transform.k8s.transformation_context import TransformationContext
from app.transform.measurement import Measurement
from app.transform.transformer_base import TransformerBase
from app.transform.upper_ontology_base import UpperOntologyBase
from app.util.quantity import parse_quantity


class WorkloadToRDFTransformer(TransformerBase, UpperOntologyBase):
    def __init__(self, source: Dict[str, Any], sink: Graph):
        TransformerBase.__init__(self, source, sink)
        UpperOntologyBase.__init__(self, sink)

    def transform(self, _: TransformationContext) -> None:
        workload_id = self.get_id()
        kind = self.source["kind"]
        self.add_assigned_task(workload_id, kind)
        if kind:
            self.add_references(workload_id, kind)
        self.add_soft_constraints(workload_id)
        self.add_hard_constraints(workload_id)
        self.add_workload_scheduler(workload_id)

    def add_soft_constraints(self, workload_id: IRI) -> None:
        self.add_resource_constraint_by_jpath(
            workload_id,
            Measurement.CPU_ALLOCATED,
            True,
            [
                [
                    "spec",
                    "template",
                    "spec",
                    "containers",
                    "resources",
                    "requests",
                    "cpu",
                ],
                [
                    "spec",
                    "template",
                    "spec",
                    "initContainers",
                    "resources",
                    "requests",
                    "cpu",
                ],
            ],
            self.UNIT_CPU_CORE_ID,
            self.ASPECT_PERFORMANCE_ID,
        )

        self.add_resource_constraint_by_jpath(
            workload_id,
            "RAM.Allocated",
            True,
            [
                [
                    "spec",
                    "template",
                    "spec",
                    "containers",
                    "resources",
                    "requests",
                    "memory",
                ],
                [
                    "spec",
                    "template",
                    "spec",
                    "initContainers",
                    "resources",
                    "requests",
                    "memory",
                ],
            ],
            self.UNIT_BYTES_ID,
            self.ASPECT_PERFORMANCE_ID,
        )

        self.add_resource_constraint_by_jpath(
            workload_id,
            Measurement.STORAGE_ALLOCATED,
            True,
            [
                [
                    "spec",
                    "template",
                    "spec",
                    "containers",
                    "resources",
                    "requests",
                    "ephemeral-storage",
                ],  # noqa: E501
                [
                    "spec",
                    "template",
                    "spec",
                    "initContainers",
                    "resources",
                    "requests",
                    "ephemeral-storage",
                ],  # noqa: E501
            ],
            self.UNIT_BYTES_ID,
            self.ASPECT_PERFORMANCE_ID,
        )

        self.add_resource_constraint_by_jpath(
            workload_id,
            Measurement.GPU_ALLOCATED,
            True,
            [
                [
                    "spec",
                    "template",
                    "metadata",
                    "annotations",
                    "glaciation-project.eu/resource/requests/gpu",
                ]  # noqa: E501
            ],
            self.UNIT_CPU_CORE_ID,
            self.ASPECT_PERFORMANCE_ID,
        )

        self.add_resource_constraint_by_jpath(
            workload_id,
            Measurement.NETWORK_ALLOCATED,
            True,
            [
                [
                    "spec",
                    "template",
                    "metadata",
                    "annotations",
                    "glaciation-project.eu/resource/requests/network",
                ]  # noqa: E501
            ],
            self.UNIT_BYTES_ID,
            self.ASPECT_PERFORMANCE_ID,
        )

        self.add_resource_constraint_by_jpath(
            workload_id,
            Measurement.ENERGY_ALLOCATED,
            True,
            [
                [
                    "spec",
                    "template",
                    "metadata",
                    "annotations",
                    "glaciation-project.eu/resource/requests/energy",
                ]  # noqa: E501
            ],
            self.UNIT_MILLIWATT_ID,
            self.ASPECT_POWER_ID,
        )

    def add_hard_constraints(self, workload_id: IRI) -> None:
        self.add_resource_constraint_by_jpath(
            workload_id,
            Measurement.CPU_CAPACITY,
            False,
            [
                [
                    "spec",
                    "template",
                    "spec",
                    "containers",
                    "resources",
                    "limits",
                    "cpu",
                ],
                [
                    "spec",
                    "template",
                    "spec",
                    "initContainers",
                    "resources",
                    "limits",
                    "cpu",
                ],
            ],
            self.UNIT_CPU_CORE_ID,
            self.ASPECT_PERFORMANCE_ID,
        )

        self.add_resource_constraint_by_jpath(
            workload_id,
            Measurement.RAM_CAPACITY,
            False,
            [
                [
                    "spec",
                    "template",
                    "spec",
                    "containers",
                    "resources",
                    "limits",
                    "memory",
                ],
                [
                    "spec",
                    "template",
                    "spec",
                    "initContainers",
                    "resources",
                    "limits",
                    "memory",
                ],
            ],
            self.UNIT_BYTES_ID,
            self.ASPECT_PERFORMANCE_ID,
        )

        self.add_resource_constraint_by_jpath(
            workload_id,
            Measurement.STORAGE_CAPACITY,
            False,
            [
                [
                    "spec",
                    "template",
                    "spec",
                    "containers",
                    "resources",
                    "limits",
                    "ephemeral-storage",
                ],  # noqa: E501
                [
                    "spec",
                    "template",
                    "spec",
                    "initContainers",
                    "resources",
                    "limits",
                    "ephemeral-storage",
                ],  # noqa: E501
            ],
            self.UNIT_BYTES_ID,
            self.ASPECT_PERFORMANCE_ID,
        )

        self.add_resource_constraint_by_jpath(
            workload_id,
            Measurement.GPU_CAPACITY,
            False,
            [
                [
                    "spec",
                    "template",
                    "metadata",
                    "annotations",
                    "glaciation-project.eu/resource/limits/gpu",
                ]  # noqa: E501
            ],
            self.UNIT_CPU_CORE_ID,
            self.ASPECT_PERFORMANCE_ID,
        )

        self.add_resource_constraint_by_jpath(
            workload_id,
            Measurement.NETWORK_CAPACITY,
            False,
            [
                [
                    "spec",
                    "template",
                    "metadata",
                    "annotations",
                    "glaciation-project.eu/resource/limits/network",
                ]  # noqa: E501
            ],
            self.UNIT_BYTES_ID,
            self.ASPECT_PERFORMANCE_ID,
        )

        self.add_resource_constraint_by_jpath(
            workload_id,
            Measurement.ENERGY_CAPACITY,
            False,
            [
                [
                    "spec",
                    "template",
                    "metadata",
                    "annotations",
                    "glaciation-project.eu/resource/limits/energy",
                ]  # noqa: E501
            ],
            self.UNIT_MILLIWATT_ID,
            self.ASPECT_POWER_ID,
        )

    def add_resource_constraint_by_jpath(
        self,
        workload_id: IRI,
        constraint_id_name: str,
        is_soft: bool,
        jqpath: List[List[str]],
        unit: IRI,
        aspect: IRI,
    ) -> None:
        constraint_id = workload_id.dot(constraint_id_name)
        value = self.get_int_quantity_value_list(jqpath)
        if value:
            self.add_constraint(
                constraint_id,
                constraint_id_name,
                is_soft,
                value,
                unit,
                aspect,
            )
            self.sink.add_relation(workload_id, self.HAS_CONSTRAINT, constraint_id)

    def add_workload_scheduler(self, workload_id: IRI) -> None:
        scheduler_name = self.get_opt_str_value(
            ["spec", "template", "spec", "schedulerName"]
        )
        scheduler_id = IRI(
            self.GLACIATION_PREFIX, scheduler_name or "default-scheduler"
        )
        self.add_scheduler(scheduler_id, None)
        self.sink.add_relation(scheduler_id, self.ASSIGNS, workload_id)

    def get_int_quantity_value_list(self, queries: List[List[str]]) -> Optional[float]:
        result = []
        for query in queries:
            values = self.get_str_list(query)
            for quantity_str in values:
                quantity = float(parse_quantity(quantity_str))
                if quantity > 0:
                    result.append(quantity)
        if len(result) > 0:
            return sum(result)
        else:
            return None
