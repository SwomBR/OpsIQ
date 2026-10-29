"""Entry point for the OpsIQ FastAPI application.

Start the server from the backend/ folder with:
    uvicorn app.main:app --reload
"""

import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.analytics import router as analytics_router
from app.api.routes import router
from app.config import settings
from app.services import analytics_service


def configure_logging(level):
    """Send log messages from OpsIQ's own code (the "app" package) to
    the terminal. Uvicorn configures its own request logs separately."""

    app_logger = logging.getLogger("app")
    app_logger.setLevel(level)

    if not app_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        app_logger.addHandler(handler)


configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run once when the server starts (before yield) and stops (after)."""

    if settings.preload_data:
        # A background thread, so the server answers health checks
        # while the analytics are being calculated.
        threading.Thread(
            target=analytics_service.warm_cache,
            name="opsiq-cache-warmup",
            daemon=True,
        ).start()

    yield


app = FastAPI(
    title="OpsIQ API",
    description="Business operations analytics API for OpsIQ.",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS lets the React dashboard, which runs on a different address
# (for example http://localhost:5173), read responses from this API.
# Only the origins listed in OPSIQ_CORS_ORIGINS are allowed, and the
# API is read-only, so only GET requests are permitted.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["Accept", "Content-Type"],
    allow_credentials=False,
)


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, error: Exception):
    """Return a short JSON error instead of exposing a stack trace.

    The full stack trace is written to the server log.
    """

    logger.exception("Unexpected error while handling %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred."},
    )


# All version 1 endpoints live under /api/v1, for example /api/v1/health.
app.include_router(router, prefix="/api/v1")

# Business analytics live under /api/v1/analytics,
# for example /api/v1/analytics/summary.
app.include_router(
    analytics_router,
    prefix="/api/v1/analytics",
    tags=["analytics"],
)

logger.info(
    "OpsIQ API ready (environment=%s, CORS origins=%s)",
    settings.environment,
    ", ".join(settings.cors_origins) or "none",
)
