from dataclasses import dataclass


@dataclass
class InfluxDBSettings:
    url: str
    token: str
    org: str
    timeout: int
