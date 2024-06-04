from pydantic_settings import BaseSettings


class K8SSettings(BaseSettings):
    in_cluster: bool
