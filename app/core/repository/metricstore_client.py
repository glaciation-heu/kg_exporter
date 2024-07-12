from typing import List

from app.core.repository.query_result_parser import QueryResultParser
from app.core.types import MetricValue


class MetricStoreClient:
    async def query(
        self, query: str, result_parser: QueryResultParser
    ) -> List[MetricValue]:
        raise NotImplementedError
