import asyncio

from app.clients.influxdb.influxdb_client import InfluxDBClient
from app.clients.k8s.k8s_client import K8SClient
from app.clients.metadata.metadata_service_client import MetadataServiceClient
from app.pipeline.dkg_slice_store import DKGSliceStore
from app.pipeline.kg_builder import KGBuilder
from app.pipeline.kg_updater import KGUpdater
from app.pipeline.source.influxdb_repository import InfluxDBRepository
from app.pipeline.source.k8s_repository import K8SRepository
from app.pipeline.source.kg_repository import KGRepository


class KGExporterContext:
    builder: KGBuilder
    updater: KGUpdater
    runner: asyncio.Runner
    dkg_slice_store: DKGSliceStore

    def __init__(
        self,
        metadata_client: MetadataServiceClient,
        k8s_client: K8SClient,
        influxdb_client: InfluxDBClient,
    ):
        kg_repository = KGRepository(metadata_client)
        k8s_repository = K8SRepository(k8s_client)
        influxdb_repository = InfluxDBRepository(influxdb_client)
        self.dkg_slice_store = DKGSliceStore()
        self.builder = KGBuilder(
            self.dkg_slice_store, k8s_repository, kg_repository, influxdb_repository
        )
        self.updater = KGUpdater(self.dkg_slice_store, kg_repository)
        self.runner = asyncio.Runner()

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
