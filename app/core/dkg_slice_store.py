from typing import Dict

from app.core.types import DKGSlice, KGSliceId


class DKGSliceStore:
    slices: Dict[KGSliceId, DKGSlice]

    def __init__(self):
        self.slices = {}

    def update(self, slice: DKGSlice) -> bool:
        existing = self.slices.get(slice.slice_id)
        if not existing or existing.graph != slice.graph:
            self.slices[slice.slice_id] = slice
            return True
        else:
            return False
