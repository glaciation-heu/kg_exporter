from typing import List, Set

from unittest import TestCase

from app.core.kg_slice_assembler import KGSliceAssembler
from app.core.test_snapshot_base import SnapshotTestBase
from app.core.types import KGSliceId
from app.kg.iri import IRI


class KGSliceAssemblerTest(TestCase, SnapshotTestBase):
    def setUp(self):
        self.maxDiff = None

    def test_assemble_empty(self) -> None:
        now = 1000
        slice_id = KGSliceId("127.0.0.1", 80)
        inputs = self.get_inputs("empty")
        assembler = KGSliceAssembler()

        actual = assembler.assemble(
            now,
            slice_id,
            inputs,
        )
        self.assertEqual(slice_id, actual.slice_id)
        self.assertEqual(now, actual.timestamp)
        self.assert_graph(actual.graph, "empty", slice_id)

    def test_assemble_minimal(self) -> None:
        now = 1000
        slice_id = KGSliceId("glaciation-test-master01", 80)
        inputs = self.get_inputs("minimal")
        assembler = KGSliceAssembler()

        actual = assembler.assemble(
            now,
            slice_id,
            inputs,
        )
        self.assertEqual(slice_id, actual.slice_id)
        self.assertEqual(now, actual.timestamp)
        self.assert_graph(actual.graph, "minimal", slice_id)

    def to_value(self, ids: List[IRI]) -> Set[str]:
        return {iri.get_value() for iri in ids}
