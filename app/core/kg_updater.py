from app.core.dkg_slice_store import DKGSliceStore
from app.core.kg_repository import KGRepository


class KGUpdater:
    dkg_slice_store: DKGSliceStore
    kg_repository: KGRepository

    def __init__(self, dkg_slice_store: DKGSliceStore, kg_repository: KGRepository):
        self.dkg_slice_store = dkg_slice_store
        self.kg_repository = kg_repository

    async def run(self) -> None:
        pass
