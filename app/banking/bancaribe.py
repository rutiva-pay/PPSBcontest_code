from app.banking.base import BankAdapter
from app.banking.schemas import C2PRequest, C2PResponse, OperationStatus


class BancaribeAdapter(BankAdapter):
    """Stub for Bancaribe C2P integration. Real implementation: Día 7."""

    @property
    def supports_aggregator_mode(self) -> bool:
        return False

    async def initiate_c2p(self, req: C2PRequest) -> C2PResponse:
        raise NotImplementedError("BancaribeAdapter.initiate_c2p — pendiente Día 7")

    async def query_operation(self, ref: str) -> OperationStatus:
        raise NotImplementedError("BancaribeAdapter.query_operation — pendiente Día 7")

    async def list_supported_banks(self) -> list[dict]:
        return [{"code": "0114", "name": "Bancaribe"}]
