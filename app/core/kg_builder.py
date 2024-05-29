from app.core.dkg_slice_store import DKGSliceStore
from app.core.influxdb_repository import InfluxDBRepository
from app.core.k8s_repository import K8SRepository
from app.core.kg_repository import KGRepository


class KGBuilder:
    dkg_slice_store: DKGSliceStore
    k8s_repository: K8SRepository
    kg_repository: KGRepository
    influxdb_repository: InfluxDBRepository

    def __init__(
        self,
        dkg_slice_store: DKGSliceStore,
        k8s_repository: K8SRepository,
        kg_repository: KGRepository,
        influxdb_repository: InfluxDBRepository,
    ):
        self.dkg_slice_store = dkg_slice_store
        self.k8s_repository = k8s_repository
        self.kg_repository = kg_repository
        self.influxdb_repository = influxdb_repository

    async def run(self) -> None:
        pass
