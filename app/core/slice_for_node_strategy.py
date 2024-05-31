from typing import List

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.slice_strategy import SliceStrategy
from app.core.types import KGSliceId


class SliceForNodeStrategy(SliceStrategy):
    def get_slices(self, snapshot: ResourceSnapshot) -> List[KGSliceId]:
        slice_id = KGSliceId("127.0.0.1", 80)
        return [slice_id]
