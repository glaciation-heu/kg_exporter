from unittest import TestCase

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.kg_slice_assembler import KGSliceAssembler
from app.core.types import KGSliceId, MetricSnapshot, SliceInputs


class KGSliceAssemblerTest(TestCase):
    def test_assemble_empty(self) -> None:
        now = 1
        slice_id = KGSliceId("127.0.0.1", 80)
        resource_snapshot = ResourceSnapshot()
        metric_snapshot = MetricSnapshot()
        inputs = SliceInputs(resource_snapshot, metric_snapshot)
        assembler = KGSliceAssembler()

        assembler.assemble(
            now,
            slice_id,
            inputs,
        )
