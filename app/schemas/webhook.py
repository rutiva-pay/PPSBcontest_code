from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class WebhookEndpointCreateRequest(BaseModel):
    url: HttpUrl
    enabled_events: List[str] = Field(default_factory=lambda: ["*"])


class WebhookEndpointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_id: str
    merchant_id: UUID
    url: str
    enabled_events: List[str]
    status: str
    created_at: datetime
    updated_at: datetime


class WebhookEndpointCreateResponse(WebhookEndpointResponse):
    signing_secret: str = Field(
        ...,
        description="Plaintext signing secret. Shown once. Store it now — not retrievable later.",
    )


class WebhookEndpointListResponse(BaseModel):
    items: List[WebhookEndpointResponse]
    next_cursor: Optional[str] = None
    has_more: bool
