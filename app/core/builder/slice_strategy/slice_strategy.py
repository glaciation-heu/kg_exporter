from typing import Dict

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.types import KGSliceId, MetricSnapshot, SliceInputs


class SliceStrategy:
    def get_slices(
        self, resources: ResourceSnapshot, metrics: MetricSnapshot
    ) -> Dict[KGSliceId, SliceInputs]:
        raise NotImplementedError
