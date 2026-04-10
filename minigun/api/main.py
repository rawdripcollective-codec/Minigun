"""Minigun FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI

from minigun.api.routers import cognition, tools, execution, apps, improvement, kernel

app = FastAPI(
    title="Minigun",
    description="Autonomous DevOps + AGI software engineer platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(cognition.router)
app.include_router(tools.router)
app.include_router(execution.router)
app.include_router(apps.router)
app.include_router(improvement.router)
app.include_router(kernel.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}
