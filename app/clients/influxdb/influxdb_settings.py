from pydantic_settings import BaseSettings


class InfluxDBSettings(BaseSettings):
    url: str
    token: str
    org: str
    timeout: int
