"""Bearer token authentication middleware."""

from __future__ import annotations

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from minigun.config import settings

logger = logging.getLogger(__name__)

# Paths that do not require authentication
_PUBLIC_PATHS = {"/", "/v1/health", "/docs", "/openapi.json", "/redoc"}


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """Validates Authorization: Bearer <token> on all non-public routes."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid Authorization header"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header[len("Bearer "):]
        if token != settings.API_SECRET_KEY:
            logger.warning("Invalid bearer token from %s", request.client)
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Invalid API token"},
            )

        return await call_next(request)
