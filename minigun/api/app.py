"""FastAPI application factory."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from minigun.api.dashboard import DASHBOARD_HTML
from minigun.api.middleware.auth import BearerTokenMiddleware
from minigun.api.routers import audit, incidents, intents, tasks
from minigun.config import settings

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    logging.basicConfig(level=settings.LOG_LEVEL)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI Minigun – Layered Planner-Solver-Critic agent platform",
    )

    # Auth middleware
    app.add_middleware(BearerTokenMiddleware)

    # Routers
    app.include_router(intents.router)
    app.include_router(tasks.router)
    app.include_router(incidents.router)
    app.include_router(audit.router)

    @app.get("/v1/health", tags=["health"])
    async def health() -> dict:
        return {"status": "ok", "version": settings.APP_VERSION}

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def dashboard() -> HTMLResponse:
        return HTMLResponse(content=DASHBOARD_HTML)

    return app


app = create_app()
