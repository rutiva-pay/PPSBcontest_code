from abc import ABC, abstractmethod

from app.banking.schemas import C2PRequest, C2PResponse, OperationStatus


class BankAdapter(ABC):
    @abstractmethod
    async def initiate_c2p(self, req: C2PRequest) -> C2PResponse:
        ...

    @abstractmethod
    async def query_operation(self, ref: str) -> OperationStatus:
        ...

    @abstractmethod
    async def list_supported_banks(self) -> list[dict]:
        ...

    @property
    @abstractmethod
    def supports_aggregator_mode(self) -> bool:
        ...
