from pydantic_settings import BaseSettings


class MetadataServiceSettings(BaseSettings):
    metadata_service_url: str = "metadata-service"
    metadata_service_push_period_sec: int = 60
