from pydantic_settings import BaseSettings


class MetadataServiceSettings(BaseSettings):
    metadata_service_url: str = "metadata-service"
    use_single_url: bool = True
    timeout_seconds: int = 20
