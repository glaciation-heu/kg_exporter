from unittest import TestCase

from app.core.kg_slice_assembler import KGSliceAssembler
from app.core.test_snapshot_base import SnapshotTestBase
from app.core.types import DKGSlice, KGSliceId
from app.kg.inmemory_graph import InMemoryGraph


class KGSliceAssemblerTest(TestCase, SnapshotTestBase):
    def test_assemble_empty(self) -> None:
        now = 1
        slice_id = KGSliceId("127.0.0.1", 80)
        inputs = self.get_inputs("empty")
        assembler = KGSliceAssembler()

        actual = assembler.assemble(
            now,
            slice_id,
            inputs,
        )
        self.assertEqual(DKGSlice(slice_id, InMemoryGraph(), now), actual)

    def test_assemble_minimal(self) -> None:
        pass
        # now = 1
        # slice_id = KGSliceId("127.0.0.1", 80)
        # inputs = self.get_inputs("minimal")
        # assembler = KGSliceAssembler()

        # actual = assembler.assemble(
        #     now,
        #     slice_id,
        #     inputs,
        # )
        # self.assertEqual(DKGSlice(slice_id, InMemoryGraph(), now), actual)

    def test_assemble_multinode(self) -> None:
        pass
