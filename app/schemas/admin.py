import re
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

_RIF_RE = re.compile(r"^[VEJGP]-\d{8}-\d$")
_BANK_CODE_RE = re.compile(r"^\d{4}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AdminMerchantCreateRequest(BaseModel):
    legal_name: str = Field(..., min_length=2, max_length=255)
    rif: str = Field(..., min_length=11, max_length=15)
    contact_email: str = Field(..., min_length=3, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    acquiring_bank: str = Field(..., description="Código de 4 dígitos del banco adquirente.")
    account_number: str = Field(..., min_length=4, max_length=64, description="Número de cuenta del comerciante (se guarda como bytes; cifrado pendiente).")
    api_key_label: str = Field(default="default key", max_length=100)
    environment: Literal["test", "live"] = "live"

    @field_validator("rif")
    @classmethod
    def _validate_rif(cls, v: str) -> str:
        norm = v.upper().strip()
        if not _RIF_RE.match(norm):
            raise ValueError("RIF debe tener formato X-XXXXXXXX-X (V/E/J/G/P).")
        return norm

    @field_validator("contact_email")
    @classmethod
    def _validate_email(cls, v: str) -> str:
        norm = v.strip().lower()
        if not _EMAIL_RE.match(norm):
            raise ValueError("Email inválido.")
        return norm

    @field_validator("acquiring_bank")
    @classmethod
    def _validate_bank(cls, v: str) -> str:
        if not _BANK_CODE_RE.match(v):
            raise ValueError("acquiring_bank debe ser código de 4 dígitos.")
        return v


class AdminMerchantCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchant_id: str
    merchant_external_id: str
    merchant_account_id: str
    api_key_id: str
    api_key: str = Field(..., description="Plaintext sk_ — devuelto UNA SOLA VEZ. Guardar inmediatamente.")
    environment: str
