from unittest import TestCase

from app.clients.influxdb.influxdb_settings import InfluxDBSettings
from app.clients.influxdb.mock_infuxdbclient import MockInfluxDBClient
from app.clients.k8s.k8s_settings import K8SSettings
from app.clients.k8s.mock_k8s_client import MockK8SClient
from app.clients.metadata_service.metadata_service_settings import (
    MetadataServiceSettings,
)
from app.clients.metadata_service.mock_metadata_service_client import (
    MockMetadataServiceClient,
)
from app.core.kg_builder import KGBuilderSettings, QuerySettings
from app.kgexporter_context import KGExporterContext
from app.kgexporter_settings import KGExporterSettings
from app.serialize.jsonld_configuration import JsonLDConfiguration


class KGExporterContextTest(TestCase):
    def test_start(self):
        metadata_client = MockMetadataServiceClient()
        k8s_client = MockK8SClient()
        influxdb_client = MockInfluxDBClient()
        jsonld_config = JsonLDConfiguration(contexts=dict(), aggregates=set())
        settings = KGExporterSettings(
            builder=KGBuilderSettings(
                builder_tick_seconds=1, influxdb_queries=QuerySettings()
            ),
            k8s=K8SSettings(in_cluster=True),
            influxdb=InfluxDBSettings(
                url="test", token="token", org="org", timeout=60000
            ),
            metadata=MetadataServiceSettings(),
        )
        context = KGExporterContext(
            metadata_client, k8s_client, influxdb_client, jsonld_config, settings
        )
        context.start()
        context.stop()
