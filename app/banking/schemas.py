from pydantic import BaseModel, Field


class C2PRequest(BaseModel):
    merchant_account: str
    customer_phone: str
    customer_id: str
    customer_bank: str
    otp: str
    amount_cents: int = Field(..., gt=0)
    currency: str
    reference: str


class C2PResponse(BaseModel):
    reference: str
    status: str


class OperationStatus(BaseModel):
    status: str
