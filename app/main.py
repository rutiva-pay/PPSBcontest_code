import os
import re
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.v1 import payments, webhook_endpoints
from app.bootstrap import seed_dev_fixtures

_CONFIRM_PATH_RE = re.compile(r"^/v1/payments/[^/]+/confirm/?$")


class WidgetCORSMiddleware(BaseHTTPMiddleware):
    """CORS abierto solo para POST/OPTIONS en /v1/payments/{id}/confirm (Widget)."""

    async def dispatch(self, request, call_next):
        path = request.url.path
        is_confirm = bool(_CONFIRM_PATH_RE.match(path))
        if is_confirm and request.method == "OPTIONS":
            return Response(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Max-Age": "600",
                },
            )
        response = await call_next(request)
        if is_confirm:
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

_sentry_dsn = os.getenv("SENTRY_DSN")
if _sentry_dsn:
    sentry_sdk.init(
        dsn=_sentry_dsn,
        environment=os.getenv("ENVIRONMENT", "development"),
        traces_sample_rate=0.1,
        send_default_pii=False,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("ENVIRONMENT", "development") != "production":
        await seed_dev_fixtures()
    yield


app = FastAPI(title="Rutiva API", lifespan=lifespan)
app.add_middleware(WidgetCORSMiddleware)

app.include_router(payments.router)
app.include_router(webhook_endpoints.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
