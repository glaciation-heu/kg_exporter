from typing import Dict, List, Set

from dataclasses import dataclass

from app.kg.graph import Graph


@dataclass
class KGSliceId:
    node_ip: str
    port: int


@dataclass
class DKGSlice:
    slice_id: KGSliceId
    graph: Graph
    timestamp: int


class DKGSliceStore:
    slices: Dict[KGSliceId, DKGSlice]
    updates: Set[KGSliceId]

    def __init__(self):
        self.slices = {}
        self.updates = set()

    def update(self, slice: DKGSlice) -> None:
        existing = self.slices.get(slice.slice_id)
        if existing != slice:
            self.slices[slice.slice_id] = slice
            self.updates.add(slice.slice_id)

    def drain_updates(self) -> List[DKGSlice]:
        to_consume = self.updates
        self.updates = set()
        return [self.slices[slice_id] for slice_id in to_consume]
