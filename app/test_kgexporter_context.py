from typing import List, Tuple

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
    SerializedGraph,
)
from app.core.kg_builder import KGBuilderSettings, QuerySettings
from app.core.test_snapshot_base import SnapshotTestBase
from app.core.types import KGSliceId
from app.kgexporter_context import KGExporterContext
from app.kgexporter_settings import KGExporterSettings, PrometheusSettings
from app.serialize.jsonld_configuration import JsonLDConfiguration


class KGExporterContextTest(TestCase, SnapshotTestBase):
    metadata_client: MockMetadataServiceClient
    k8s_client: MockK8SClient
    influxdb_client: MockInfluxDBClient
    jsonld_config: JsonLDConfiguration
    settings: KGExporterSettings
    context: KGExporterContext

    def setUp(self) -> None:
        self.metadata_client = MockMetadataServiceClient()
        self.k8s_client = MockK8SClient()
        self.influxdb_client = MockInfluxDBClient()
        self.jsonld_config = self.get_test_jsonld_config()
        self.settings = self.test_kg_exporter_settings()
        self.context = KGExporterContext(
            self.metadata_client,
            self.k8s_client,
            self.influxdb_client,
            self.jsonld_config,
            self.settings,
        )

    def test_end_to_end_minimal(self) -> None:
        self.mock_inputs(
            "minimal",
            self.k8s_client,
            self.influxdb_client,
            self.settings.builder.queries,
        )
        self.context.start()

        inserts = self.metadata_client.wait_for_inserts2(self.context.runner, 2, 1)

        self.assert_graphs("minimal", inserts)

        self.context.stop()

    def test_end_to_end_multinode(self) -> None:
        self.settings.prometheus.endpoint_port = 8081
        self.mock_inputs(
            "multinode",
            self.k8s_client,
            self.influxdb_client,
            self.settings.builder.queries,
        )
        self.context.start()

        inserts = self.metadata_client.wait_for_inserts2(self.context.runner, 2, 2)

        self.assert_graphs("multinode", inserts)

        self.context.stop()

    def assert_graphs(
        self, snapshot_identity: str, inserts: List[Tuple[str, SerializedGraph]]
    ) -> None:
        for insert in inserts:
            host_and_port, serialized_graph = insert
            slice_id = KGSliceId.from_host_port(host_and_port)
            self.assert_serialized_graph(snapshot_identity, slice_id, serialized_graph)

    def test_kg_exporter_settings(self) -> KGExporterSettings:
        settings = KGExporterSettings(
            builder=KGBuilderSettings(
                builder_tick_seconds=1, node_port=80, queries=QuerySettings()
            ),
            k8s=K8SSettings(in_cluster=True),
            influxdb=InfluxDBSettings(
                url="test", token="token", org="org", timeout=60000
            ),
            metadata=MetadataServiceSettings(),
            prometheus=PrometheusSettings(endpoint_port=8080),
        )
        return settings