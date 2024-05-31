from unittest import TestCase

from app.clients.influxdb.mock_infuxdbclient import MockInfluxDBClient
from app.clients.k8s.mock_k8s_client import MockK8SClient
from app.clients.metadata_service.mock_metadata_service_client import (
    MockMetadataServiceClient,
)
from app.context import KGExporterContext
from app.serialize.jsonld_configuration import JsonLDConfiguration


class KGExporterContextTest(TestCase):
    def test_start(self):
        metadata_client = MockMetadataServiceClient()
        k8s_client = MockK8SClient()
        influxdb_client = MockInfluxDBClient()
        jsonld_config = JsonLDConfiguration(contexts=dict(), aggregates=set())
        context = KGExporterContext(
            metadata_client, k8s_client, influxdb_client, jsonld_config
        )
        context.start()
        context.stop()
