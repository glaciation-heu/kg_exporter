from typing import Any, Dict

from app.kg.graph import Graph
from app.kg.iri import IRI
from app.transform.k8s.transformation_context import TransformationContext
from app.transform.k8s.transformer_base import TransformerBase
from app.transform.k8s.upper_ontology_base import UpperOntologyBase


class NodesToRDFTransformer(TransformerBase, UpperOntologyBase):
    def __init__(self, source: Dict[str, Any], sink: Graph):
        TransformerBase.__init__(self, source, sink)
        UpperOntologyBase.__init__(self, sink)

    def transform(self, context: TransformationContext) -> None:
        node_id = self.get_node_id(self.source)
        self.add_work_producing_resource(node_id, "KubernetesWorkerNode")

        self.add_cpu_resource(node_id, context.get_timestamp())
        self.add_memory_resource(node_id, context.get_timestamp())
        self.add_storage_resource(node_id, context.get_timestamp())
        self.add_network_resource(node_id, context.get_timestamp())
        self.add_gpu_resource(node_id, context.get_timestamp())
        self.add_energy_information(node_id, context.get_timestamp())
        self.add_node_status(node_id)

    def add_cpu_resource(self, node_id: IRI, timestamp: int) -> None:
        cpu_id = node_id.dot("CPU")
        self.add_work_producing_resource(cpu_id, "CPU")
        self.sink.add_relation(node_id, self.HAS_SUBRESOURCE, cpu_id)
        cpu_capacity_value = self.get_opt_int_quantity_value(
            ["status", "allocatable", "cpu"]
        )
        if cpu_capacity_value:
            cpu_capacity_id = cpu_id.dot("Capacity")
            self.add_measurement(
                cpu_id.dot("Capacity"),
                "Capacity CPU",
                cpu_capacity_value,
                timestamp,
                self.UNIT_CPU_CORE_ID,
                self.PROPERTY_CPU_CAPACITY,
                self.MEASURING_RESOURCE_NODE_K8S_SPEC_ID,
            )
            self.sink.add_relation(cpu_id, self.HAS_MEASUREMENT, cpu_capacity_id)

    def add_memory_resource(self, node_id: IRI, timestamp: int) -> None:
        ram_id = node_id.dot("RAM")
        self.add_work_producing_resource(ram_id, "RAM")
        self.sink.add_relation(node_id, self.HAS_SUBRESOURCE, ram_id)

        ram_capacity_value = self.get_opt_int_quantity_value(
            ["status", "allocatable", "memory"]
        )
        if ram_capacity_value:
            ram_capacity_id = ram_id.dot("Capacity")
            self.add_measurement(
                ram_capacity_id,
                "Capacity",
                ram_capacity_value,
                timestamp,
                self.UNIT_BYTES_ID,
                self.PROPERTY_RAM_CAPACITY,
                self.MEASURING_RESOURCE_NODE_K8S_SPEC_ID,
            )
            self.sink.add_relation(ram_id, self.HAS_MEASUREMENT, ram_capacity_id)

    def add_storage_resource(self, node_id: IRI, timestamp: int) -> None:
        storage_id = node_id.dot("Storage")
        self.add_work_producing_resource(storage_id, "EphemeralStorage")
        self.sink.add_relation(node_id, self.HAS_SUBRESOURCE, storage_id)

        storage_capacity_value = self.get_opt_int_quantity_value(
            ["status", "allocatable", "ephemeral-storage"]
        )
        if storage_capacity_value:
            storage_capacity_id = storage_id.dot("Capacity")
            self.add_measurement(
                storage_capacity_id,
                "Capacity",
                storage_capacity_value,
                timestamp,
                self.UNIT_BYTES_ID,
                self.PROPERTY_STORAGE_CAPACITY,
                self.MEASURING_RESOURCE_NODE_K8S_SPEC_ID,
            )
            self.sink.add_relation(
                storage_id, self.HAS_MEASUREMENT, storage_capacity_id
            )

    def add_network_resource(self, node_id: IRI, _: int) -> None:
        storage_id = node_id.dot("Network")
        self.add_work_producing_resource(storage_id, "Network")
        self.sink.add_relation(node_id, self.HAS_SUBRESOURCE, storage_id)

    def add_gpu_resource(self, node_id: IRI, _: int) -> None:
        storage_id = node_id.dot("GPU")
        self.add_work_producing_resource(storage_id, "GPU")
        self.sink.add_relation(node_id, self.HAS_SUBRESOURCE, storage_id)

    def add_energy_information(self, node_id: IRI, timestamp: int) -> None:
        energy_index_value = self.get_opt_int_quantity_value(
            [
                "metadata",
                "annotations",
                "glaciation-project.eu/metric/node-energy-index",
            ]
        )
        if energy_index_value:
            energy_index_id = node_id.dot("Energy.Index")
            self.add_measurement(
                energy_index_id,
                "Energy.Index",
                energy_index_value,
                timestamp,
                self.UNIT_MILLIWATT_ID,
                self.PROPERTY_ENERGY_INDEX,
                self.MEASURING_RESOURCE_NODE_K8S_SPEC_ID,
            )
            self.sink.add_relation(node_id, self.HAS_MEASUREMENT, energy_index_id)

    def add_node_status(self, node_id: IRI) -> None:
        status_value = self.get_node_status()
        last_transition_time = (
            self.get_str_value(
                '$.status.conditions[?type == "Ready"].lastTransitionTime'
            )
            or "0"
        )
        status_id = node_id.dot("Status")
        self.add_status(status_id, status_value, last_transition_time, None)
        self.sink.add_relation(node_id, self.HAS_STATUS, status_id)

    def get_node_status(self) -> str:
        status = self.get_str_value('$.status.conditions[?type == "Ready"].status')
        if status and status.lower() == "true":
            return "Ready"
        elif status and status.lower() == "false":
            return "NotReady"
        else:
            return "Unknown"
