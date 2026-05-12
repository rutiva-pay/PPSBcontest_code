import asyncio
import random
import uuid

from app.banking.base import BankAdapter
from app.banking.schemas import C2PRequest, C2PResponse, OperationStatus


SUPPORTED_BANKS: list[dict] = [
    {"code": "0114", "name": "Bancaribe"},
    {"code": "0191", "name": "BNC"},
    {"code": "0105", "name": "Mercantil"},
    {"code": "0102", "name": "Banco de Venezuela"},
    {"code": "0108", "name": "Provincial"},
]

SUPPORTED_BANK_CODES: frozenset[str] = frozenset(b["code"] for b in SUPPORTED_BANKS)


class MockBankAdapter(BankAdapter):
    @property
    def supports_aggregator_mode(self) -> bool:
        return False

    async def initiate_c2p(self, req: C2PRequest) -> C2PResponse:
        await asyncio.sleep(random.uniform(1.0, 3.0))
        if random.random() < 0.8:
            return C2PResponse(
                reference=f"MOCK-{uuid.uuid4().hex[:12].upper()}",
                status="aprobado",
            )
        raise ValueError("fondos_insuficientes")

    async def query_operation(self, ref: str) -> OperationStatus:
        await asyncio.sleep(random.uniform(0.2, 0.8))
        return OperationStatus(status="aprobado")

    async def list_supported_banks(self) -> list[dict]:
        return list(SUPPORTED_BANKS)
