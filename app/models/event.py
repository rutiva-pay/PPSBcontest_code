from datetime import datetime
from typing import Any

from sqlalchemy import String, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    external_id: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    related_entity_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=True)
    related_entity_type: Mapped[str] = mapped_column(String(50), nullable=True)
    actor_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default='{}')
    ip_address: Mapped[str] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
