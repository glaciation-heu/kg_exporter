from typing import Dict

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.slice_strategy import SliceStrategy
from app.core.types import KGSliceId, MetricSnapshot, SliceInputs


class SliceForNodeStrategy(SliceStrategy):
    def get_slices(
        self, resources: ResourceSnapshot, metrics: MetricSnapshot
    ) -> Dict[KGSliceId, SliceInputs]:
        slice_id = KGSliceId("127.0.0.1", 80)
        return {slice_id: SliceInputs(resources, metrics)}
