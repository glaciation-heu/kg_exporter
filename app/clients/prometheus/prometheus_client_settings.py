from pydantic_settings import BaseSettings


class PrometheusClientSettings(BaseSettings):
    url: str
