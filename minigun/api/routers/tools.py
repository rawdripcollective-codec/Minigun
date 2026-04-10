"""Tools router: /api/v1/tools/*"""

from __future__ import annotations

from fastapi import APIRouter
from typing import Any

from minigun.api.schemas.kernel import ToolExecuteRequest, ToolResultSchema
import minigun.tools.mcp  # noqa: F401 – triggers auto-registration
from minigun.tools.registry import ToolRegistry

router = APIRouter(prefix="/api/v1/tools", tags=["tools"])


@router.get("/")
async def list_tools() -> list[dict[str, Any]]:
    return ToolRegistry.list_tools()


@router.post("/execute", response_model=ToolResultSchema)
async def execute_tool(req: ToolExecuteRequest) -> ToolResultSchema:
    result = await ToolRegistry.execute(req.name, req.params)
    return ToolResultSchema(success=result.success, data=result.data, error=result.error)
