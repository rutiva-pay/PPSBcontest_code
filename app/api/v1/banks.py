import time

from fastapi import APIRouter, Depends

from app.api.deps import get_bank_adapter
from app.banking.base import BankAdapter

router = APIRouter(prefix="/v1/banks", tags=["banks"])

_CACHE_TTL_SECONDS = 3600
_cache: dict[str, object] = {"expires_at": 0.0, "data": None}


@router.get(
    "",
    summary="Listar bancos soportados",
    description="Lista pública de bancos venezolanos soportados. CORS abierto: el Widget la consume sin autenticación.",
)
async def list_banks(bank: BankAdapter = Depends(get_bank_adapter)) -> dict:
    now = time.monotonic()
    if _cache["data"] is None or now >= _cache["expires_at"]:
        _cache["data"] = await bank.list_supported_banks()
        _cache["expires_at"] = now + _CACHE_TTL_SECONDS
    return {"object": "list", "data": _cache["data"]}
