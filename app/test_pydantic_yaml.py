from tempfile import TemporaryDirectory
from unittest import TestCase

from app.clients.influxdb.influxdb_settings import InfluxDBSettings
from app.clients.k8s.k8s_settings import K8SSettings
from app.clients.metadata_service.metadata_service_settings import (
    MetadataServiceSettings,
)
from app.core.kg_builder import KGBuilderSettings, QuerySettings
from app.kgexporter_settings import KGExporterSettings
from app.pydantic_yaml import from_yaml, to_yaml


class PyDanticYamlTest(TestCase):
    def test_dump_load_settings(self):
        expected = KGExporterSettings(
            builder=KGBuilderSettings(
                builder_tick_seconds=1, node_port=80, queries=QuerySettings()
            ),
            k8s=K8SSettings(in_cluster=True),
            influxdb=InfluxDBSettings(
                url="test", token="token", org="org", timeout=60000
            ),
            metadata=MetadataServiceSettings(),
        )
        with TemporaryDirectory("-pydantic", "test") as tmpdir:
            yaml_file = f"{tmpdir}/test.yaml"
            to_yaml(yaml_file, expected)
            actual = from_yaml(yaml_file, KGExporterSettings)

        self.assertEqual(expected, actual)
