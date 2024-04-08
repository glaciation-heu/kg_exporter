from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    metadata_service_url: str = "http://metadata.integration/api/v0/graph"
    metadata_service_push_period_sec: int = 60
