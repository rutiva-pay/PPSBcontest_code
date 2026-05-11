from datetime import datetime
from typing import Any, List

from sqlalchemy import String, Boolean, ForeignKey, text, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB, BYTEA
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    external_id: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    signing_secret_encrypted: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    enabled_events: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, server_default='{"*"}')
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="active")
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))


class WebhookAttempt(Base):
    __tablename__ = "webhook_attempts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    webhook_endpoint_id: Mapped[str] = mapped_column(ForeignKey("webhook_endpoints.id"), nullable=False)
    payment_intent_id: Mapped[str] = mapped_column(ForeignKey("payment_intents.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    attempt_number: Mapped[int] = mapped_column(nullable=False, server_default="1")
    response_status: Mapped[int] = mapped_column(nullable=True)
    response_body: Mapped[str] = mapped_column(String, nullable=True)
    delivered: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    next_retry_at: Mapped[datetime] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    delivered_at: Mapped[datetime] = mapped_column(nullable=True)
