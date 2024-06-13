from pydantic_settings import BaseSettings

from app.clients.influxdb.influxdb_settings import InfluxDBSettings
from app.clients.k8s.k8s_settings import K8SSettings
from app.clients.metadata_service.metadata_service_settings import (
    MetadataServiceSettings,
)
from app.core.kg_builder import KGBuilderSettings


class KGExporterSettings(BaseSettings):
    builder: KGBuilderSettings
    k8s: K8SSettings
    influxdb: InfluxDBSettings
    metadata: MetadataServiceSettings