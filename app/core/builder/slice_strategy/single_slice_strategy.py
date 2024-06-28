from typing import Dict

from urllib.parse import urlparse

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.builder.slice_strategy.slice_strategy import SliceStrategy
from app.core.types import KGSliceId, MetricSnapshot, SliceInputs


class SingleSliceStrategy(SliceStrategy):
    metadata_host: str
    metadata_port: int

    def __init__(self, metadata_url: str):
        # TODO parse
        # result = urllib.parse.urlsplit(f"//{host_and_port}")
        parse_result = urlparse(metadata_url)
        self.metadata_host = parse_result.hostname or "unknown"
        self.metadata_port = parse_result.port or 80

    def get_slices(
        self, resources: ResourceSnapshot, metrics: MetricSnapshot
    ) -> Dict[KGSliceId, SliceInputs]:
        result: Dict[KGSliceId, SliceInputs] = dict()
        slice_id = KGSliceId(self.metadata_host, self.metadata_port)
        result[slice_id] = SliceInputs(resources, metrics)
        return result
