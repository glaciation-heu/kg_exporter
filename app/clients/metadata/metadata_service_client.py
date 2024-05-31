from typing import List

from dataclasses import dataclass


@dataclass
class Triple:
    subject: str
    relation: str
    object: str


class MetadataServiceClient:
    async def query(self, host_and_port: str, sparql: str) -> List[Triple]:
        raise NotImplementedError

    async def insert(self, host_and_port: str, message: str) -> None:
        raise NotImplementedError
