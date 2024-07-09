from pydantic_settings import BaseSettings

from app.clients.k8s.k8s_settings import K8SSettings
from app.clients.metadata_service.metadata_service_settings import (
    MetadataServiceSettings,
)
from app.clients.prometheus.prometheus_client_settings import PrometheusClientSettings
from app.core.builder.kg_builder import KGBuilderSettings


class PrometheusSettings(BaseSettings):
    endpoint_port: int = 8080


class KGExporterSettings(BaseSettings):
    builder: KGBuilderSettings
    k8s: K8SSettings
    metadata: MetadataServiceSettings
    prometheus_client: PrometheusClientSettings
    prometheus: PrometheusSettings
