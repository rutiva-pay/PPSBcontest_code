import secrets
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event


def _new_event_external_id() -> str:
    return f"evt_{secrets.token_urlsafe(16)}"


class EventService:
    @staticmethod
    async def record(
        session: AsyncSession,
        event_type: str,
        payload: dict[str, Any],
        related_entity_id: Optional[UUID] = None,
        related_entity_type: Optional[str] = None,
        actor_id: Optional[UUID] = None,
        actor_type: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Event:
        event = Event(
            external_id=_new_event_external_id(),
            event_type=event_type,
            related_entity_id=related_entity_id,
            related_entity_type=related_entity_type,
            actor_id=actor_id,
            actor_type=actor_type,
            payload=payload,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        session.add(event)
        await session.flush()
        return event
