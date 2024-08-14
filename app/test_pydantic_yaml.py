from tempfile import TemporaryDirectory
from unittest import TestCase

from app.clients.k8s.k8s_settings import K8SSettings
from app.clients.metadata_service.metadata_service_settings import (
    MetadataServiceSettings,
)
from app.clients.prometheus.prometheus_client_settings import PrometheusClientSettings
from app.core.builder.kg_builder import KGBuilderSettings
from app.core.repository.query_settings import QuerySettings
from app.core.repository.types import Aggregation, MetricQuery, ResultParserId
from app.kgexporter_settings import KGExporterSettings, PrometheusSettings
from app.pydantic_yaml import from_yaml, to_yaml


class PyDanticYamlTest(TestCase):
    def test_dump_load_settings(self):
        expected = KGExporterSettings(
            builder=KGBuilderSettings(
                builder_tick_seconds=1,
                node_port=80,
                queries=QuerySettings(
                    pod_queries=[
                        MetricQuery(
                            measurement_id="id",
                            subresource="subresource",
                            aggregation=Aggregation(function="sum", period_seconds=2),
                            source="source",
                            unit="unit",
                            property="property",
                            query="query",
                            result_parser=ResultParserId.PROMETHEUS_PARSER,
                        )
                    ],
                    node_queries=[
                        MetricQuery(
                            measurement_id="id",
                            subresource=None,
                            aggregation=None,
                            source="source",
                            unit="unit",
                            property="property",
                            query="query",
                            result_parser=ResultParserId.PROMETHEUS_PARSER,
                        )
                    ],
                ),
                is_single_slice=True,
                single_slice_url="metadata-service:80",
            ),
            k8s=K8SSettings(in_cluster=True),
            metadata=MetadataServiceSettings(timeout_seconds=20),
            prometheus=PrometheusSettings(endpoint_port=8080),
            prometheus_client=PrometheusClientSettings(url="prometheus.integration"),
        )
        with TemporaryDirectory("-pydantic", "test") as tmpdir:
            yaml_file = f"{tmpdir}/test.yaml"
            to_yaml(yaml_file, expected)
            actual = from_yaml(yaml_file, KGExporterSettings)

        self.assertEqual(expected, actual)
