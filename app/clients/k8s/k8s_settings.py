from dataclasses import dataclass


@dataclass
class K8SSettings:
    in_cluster: bool
