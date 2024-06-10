from typing import List

import argparse

from app.clients.influxdb.influxdb_client_impl import InfluxDBClientImpl
from app.clients.influxdb.influxdb_settings import InfluxDBSettings
from app.clients.k8s.k8s_client_impl import K8SClientImpl
from app.clients.k8s.k8s_settings import K8SSettings
from app.clients.metadata_service.metadata_service_client_impl import (
    MetadataServiceClientImpl,
)
from app.clients.metadata_service.metadata_service_settings import (
    MetadataServiceSettings,
)
from app.core.kg_builder import KGBuilderSettings, QuerySettings
from app.kgexporter_context import KGExporterContext
from app.kgexporter_settings import KGExporterSettings
from app.serialize.jsonld_configuration import JsonLDConfiguration


class KGExporterContextBuilder:
    args: List[str]

    def __init__(self, args: List[str]):
        self.args = args

    def build(self) -> KGExporterContext:
        settings = self.get_settings()
        metadata_client = MetadataServiceClientImpl(settings.metadata)
        k8s_client = K8SClientImpl(settings.k8s)
        influxdb_client = InfluxDBClientImpl(settings.influxdb)
        jsonld_config = JsonLDConfiguration(contexts=dict(), aggregates=set())

        context = KGExporterContext(
            metadata_client, k8s_client, influxdb_client, jsonld_config, settings
        )
        return context

    def get_settings(self) -> KGExporterSettings:
        return KGExporterSettings(
            builder=KGBuilderSettings(builder_tick_seconds=1, queries=QuerySettings()),
            k8s=K8SSettings(in_cluster=True),
            influxdb=InfluxDBSettings(
                url="test", token="token", org="org", timeout=60000
            ),
            metadata=MetadataServiceSettings(),
        )

    def parse(self):
        parser = argparse.ArgumentParser(description="Kubernetes watcher service")
        parser.add_argument(
            "--config",
            dest="config",
            action="store",
            help="Configuration of the KGExporter",
        )
        args = parser.parse_args()
        print(args)

        # logger = logging.getLogger()
        # logger.setLevel(logging.INFO)
        # console_handler = logging.StreamHandler()
        # logger.addHandler(console_handler)
