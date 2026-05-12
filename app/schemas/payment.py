from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreateRequest(BaseModel):
    amount: int = Field(..., gt=0)
    currency: Literal["VES", "USD"]
    customer_phone: str = Field(..., min_length=7, max_length=20)
    customer_id_document: str = Field(..., min_length=5, max_length=15)
    customer_bank_code: str = Field(..., min_length=4, max_length=8)


class PaymentConfirmRequest(BaseModel):
    client_secret: Optional[str] = None
    otp: str = Field(..., min_length=4, max_length=12)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_id: str
    merchant_id: UUID
    merchant_account_id: UUID
    amount_cents: int
    currency: str
    status: str
    customer_phone: str
    customer_id_document: str
    customer_bank_code: str
    flow_mode: str
    bank_reference: Optional[str] = None
    failure_code: Optional[str] = None
    failure_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None
    succeeded_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None


class PaymentCreateResponse(PaymentResponse):
    client_secret: Optional[str] = None


class PaymentListResponse(BaseModel):
    items: List[PaymentResponse]
    next_cursor: Optional[str] = None
    has_more: bool
