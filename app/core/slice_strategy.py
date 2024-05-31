from typing import List

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.types import KGSliceId


class SliceStrategy:
    def get_slices(self, snapshot: ResourceSnapshot) -> List[KGSliceId]:
        raise NotImplementedError
