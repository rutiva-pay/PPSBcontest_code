import base64
import secrets
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthContext, get_auth_context
from app.database import get_db
from app.models import WebhookEndpoint
from app.schemas.webhook import (
    WebhookEndpointCreateRequest,
    WebhookEndpointCreateResponse,
    WebhookEndpointListResponse,
    WebhookEndpointResponse,
)
from app.services.events import EventService
from app.services.webhooks import WebhookService, generate_signing_secret

router = APIRouter(prefix="/v1/webhook_endpoints", tags=["webhooks"])


def _new_external_id() -> str:
    return f"whep_{secrets.token_urlsafe(12)}"


def _encode_cursor(created_at: datetime, eid: UUID) -> str:
    raw = f"{created_at.isoformat()}|{eid}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")


def _decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    pad = "=" * (-len(cursor) % 4)
    try:
        raw = base64.urlsafe_b64decode(cursor + pad).decode("utf-8")
        ca_iso, id_str = raw.split("|", 1)
        return datetime.fromisoformat(ca_iso), UUID(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_cursor")


@router.post(
    "",
    response_model=WebhookEndpointCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_webhook_endpoint(
    payload: WebhookEndpointCreateRequest,
    background: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_auth_context),
) -> WebhookEndpointCreateResponse:
    secret_plaintext = generate_signing_secret()

    endpoint = WebhookEndpoint(
        external_id=_new_external_id(),
        merchant_id=auth.merchant_id,
        url=str(payload.url),
        signing_secret_encrypted=secret_plaintext.encode("utf-8"),
        enabled_events=payload.enabled_events,
        status="active",
    )
    db.add(endpoint)
    await db.flush()

    await EventService.record(
        db,
        event_type="webhook_endpoint.created",
        payload={
            "id": str(endpoint.id),
            "external_id": endpoint.external_id,
            "url": endpoint.url,
            "enabled_events": endpoint.enabled_events,
        },
        related_entity_id=endpoint.id,
        related_entity_type="webhook_endpoint",
        actor_id=auth.api_key_id,
        actor_type="api_key",
    )

    await db.commit()
    await db.refresh(endpoint)

    base = WebhookEndpointResponse.model_validate(endpoint).model_dump()
    return WebhookEndpointCreateResponse(**base, signing_secret=secret_plaintext)


@router.get("", response_model=WebhookEndpointListResponse)
async def list_webhook_endpoints(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_auth_context),
) -> WebhookEndpointListResponse:
    stmt = select(WebhookEndpoint).where(WebhookEndpoint.merchant_id == auth.merchant_id)
    if cursor:
        ca, cid = _decode_cursor(cursor)
        stmt = stmt.where(
            or_(
                WebhookEndpoint.created_at < ca,
                and_(WebhookEndpoint.created_at == ca, WebhookEndpoint.id < cid),
            )
        )
    stmt = stmt.order_by(
        WebhookEndpoint.created_at.desc(), WebhookEndpoint.id.desc()
    ).limit(limit + 1)

    res = await db.execute(stmt)
    rows = list(res.scalars().all())
    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor = (
        _encode_cursor(items[-1].created_at, items[-1].id) if has_more and items else None
    )
    return WebhookEndpointListResponse(
        items=[WebhookEndpointResponse.model_validate(it) for it in items],
        next_cursor=next_cursor,
        has_more=has_more,
    )
