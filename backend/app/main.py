from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api.health import router as health_router
from app.api.routes import router as jobs_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.database import init_db
from app.services.cleanup_service import cleanup_loop
from app.services.model_service import ModelService


logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Create configured FastAPI application instance."""
    configure_logging()
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings.ensure_directories()
        init_db()

        model_service = ModelService(settings)
        model_service.load_models()

        app.state.settings = settings
        app.state.model_service = model_service
        app.state.started_at = datetime.now(timezone.utc)

        stop_event = asyncio.Event()
        cleanup_task = asyncio.create_task(cleanup_loop(settings, stop_event))
        app.state.cleanup_stop_event = stop_event
        app.state.cleanup_task = cleanup_task

        yield

        stop_event.set()
        cleanup_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.include_router(health_router)
    app.include_router(jobs_router)

    @app.exception_handler(Exception)
    async def safe_internal_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled backend error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
        )

    return app


app = create_application()
