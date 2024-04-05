from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    metadata_service_url: str
    metadata_service_demo_message_period_sec: int = 60

    class Config:
        env_file = ".env"