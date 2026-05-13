import hmac
import os
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ApiKey, Merchant, MerchantAccount
from app.schemas.admin import (
    AdminMerchantCreateRequest,
    AdminMerchantCreateResponse,
)
from app.security import hash_api_key

router = APIRouter(prefix="/v1/admin", tags=["admin"], include_in_schema=False)


def _admin_token_required(x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")) -> None:
    """Compara X-Admin-Token contra env ADMIN_TOKEN en tiempo constante.

    Si ADMIN_TOKEN no está seteado en env, todos los endpoints admin se rechazan.
    """
    expected = os.getenv("ADMIN_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="admin_disabled")
    if not x_admin_token or not hmac.compare_digest(x_admin_token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_admin_token",
        )


def _new_merchant_external_id() -> str:
    return f"merch_{secrets.token_urlsafe(10)}"


def _new_api_key_external_id() -> str:
    return f"ak_{secrets.token_urlsafe(8)}"


def _new_api_key_plaintext(environment: str) -> str:
    return f"sk_{environment}_{secrets.token_urlsafe(28)}"


@router.post(
    "/merchants",
    response_model=AdminMerchantCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_admin_token_required)],
    summary="Crear merchant + cuenta + API key (admin)",
)
async def create_merchant(
    payload: AdminMerchantCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> AdminMerchantCreateResponse:
    """Crea un merchant nuevo con cuenta default y API key inicial.

    Idempotencia por `rif`: si ya existe un merchant con ese RIF, devuelve 409.
    El plaintext de la API key se devuelve UNA SOLA VEZ en la respuesta.
    """
    res = await db.execute(select(Merchant).where(Merchant.rif == payload.rif))
    if res.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="merchant_rif_exists")

    merchant = Merchant(
        external_id=_new_merchant_external_id(),
        legal_name=payload.legal_name,
        rif=payload.rif,
        contact_email=payload.contact_email,
        contact_phone=payload.contact_phone,
        status="active",
    )
    db.add(merchant)
    await db.flush()

    account = MerchantAccount(
        merchant_id=merchant.id,
        acquiring_bank=payload.acquiring_bank,
        account_type="merchant_direct",
        account_number_encrypted=payload.account_number.encode("utf-8"),
        is_default=True,
        status="active",
    )
    db.add(account)
    await db.flush()

    plaintext = _new_api_key_plaintext(payload.environment)
    api_key = ApiKey(
        merchant_id=merchant.id,
        external_id=_new_api_key_external_id(),
        key_hash=hash_api_key(plaintext),
        key_type="secret",
        environment=payload.environment,
        label=payload.api_key_label,
    )
    db.add(api_key)

    await db.commit()
    await db.refresh(merchant)
    await db.refresh(account)
    await db.refresh(api_key)

    return AdminMerchantCreateResponse(
        merchant_id=str(merchant.id),
        merchant_external_id=merchant.external_id,
        merchant_account_id=str(account.id),
        api_key_id=str(api_key.id),
        api_key=plaintext,
        environment=payload.environment,
    )
