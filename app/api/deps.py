from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.banking.base import BankAdapter
from app.banking.mock import MockBankAdapter
from app.database import get_db
from app.models import ApiKey, MerchantAccount
from app.security import hash_api_key


@dataclass
class AuthContext:
    merchant_id: UUID
    merchant_account_id: UUID
    api_key_id: UUID


def _extract_key(authorization: str | None, x_api_key: str | None) -> str:
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token:
            return token.strip()
    if x_api_key:
        return x_api_key.strip()
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="missing_api_key",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_auth_context(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    plaintext = _extract_key(authorization, x_api_key)
    key_hash = hash_api_key(plaintext)

    res = await db.execute(select(ApiKey).where(ApiKey.key_hash == key_hash))
    api_key = res.scalar_one_or_none()
    if api_key is None or api_key.revoked_at is not None:
        raise HTTPException(status_code=401, detail="invalid_api_key")

    res = await db.execute(
        select(MerchantAccount).where(
            MerchantAccount.merchant_id == api_key.merchant_id,
            MerchantAccount.is_default.is_(True),
            MerchantAccount.status == "active",
        )
    )
    account = res.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=403, detail="no_default_account")

    api_key.last_used_at = datetime.utcnow()
    await db.commit()

    return AuthContext(
        merchant_id=api_key.merchant_id,
        merchant_account_id=account.id,
        api_key_id=api_key.id,
    )


async def get_bank_adapter() -> BankAdapter:
    return MockBankAdapter()
