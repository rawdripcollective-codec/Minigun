"""Tests for the tools layer."""

import pytest
from minigun.tools.registry import ToolRegistry
import minigun.tools.mcp  # noqa: F401 – triggers registration


# ── Registry ───────────────────────────────────────────────────────────────

def test_registry_has_all_tools():
    tool_names = {t["name"] for t in ToolRegistry.list_tools()}
    assert tool_names >= {"browser", "git", "cloud", "vault", "code_search"}


def test_registry_get_tool():
    tool = ToolRegistry.get("browser")
    assert tool is not None
    assert tool.name == "browser"


def test_registry_get_missing():
    assert ToolRegistry.get("nonexistent") is None


# ── Browser ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_browser_navigate():
    result = await ToolRegistry.execute("browser", {"action": "navigate", "url": "https://test.com"})
    assert result.success is True
    assert result.data["status_code"] == 200


@pytest.mark.asyncio
async def test_browser_screenshot():
    result = await ToolRegistry.execute("browser", {"action": "screenshot"})
    assert result.success is True
    assert "base64" in result.data


@pytest.mark.asyncio
async def test_browser_extract_text():
    result = await ToolRegistry.execute("browser", {"action": "extract_text", "selector": "h1"})
    assert result.success is True
    assert "h1" in result.data["text"]


@pytest.mark.asyncio
async def test_browser_unknown_action():
    result = await ToolRegistry.execute("browser", {"action": "hack"})
    assert result.success is False


# ── Git ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_git_status():
    result = await ToolRegistry.execute("git", {"action": "status"})
    assert result.success is True
    assert "branch" in result.data


@pytest.mark.asyncio
async def test_git_clone():
    result = await ToolRegistry.execute("git", {"action": "clone", "repo_url": "https://github.com/x/y.git"})
    assert result.success is True
    assert "cloned_to" in result.data


@pytest.mark.asyncio
async def test_git_commit():
    result = await ToolRegistry.execute("git", {"action": "commit", "message": "test commit"})
    assert result.success is True
    assert result.data["message"] == "test commit"


@pytest.mark.asyncio
async def test_git_diff():
    result = await ToolRegistry.execute("git", {"action": "diff"})
    assert result.success is True
    assert "diff" in result.data


@pytest.mark.asyncio
async def test_git_push():
    result = await ToolRegistry.execute("git", {"action": "push"})
    assert result.success is True


# ── Cloud ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cloud_list_resources():
    result = await ToolRegistry.execute("cloud", {"action": "list_resources", "service": "compute"})
    assert result.success is True
    assert "resources" in result.data


@pytest.mark.asyncio
async def test_cloud_create_resource():
    result = await ToolRegistry.execute("cloud", {"action": "create_resource", "service": "storage", "spec": {"name": "my-bucket"}})
    assert result.success is True
    assert "id" in result.data


@pytest.mark.asyncio
async def test_cloud_delete_resource():
    result = await ToolRegistry.execute("cloud", {"action": "delete_resource", "id": "res-001"})
    assert result.success is True
    assert result.data["status"] == "deleted"


# ── Vault ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_vault_set_and_get():
    result = await ToolRegistry.execute("vault", {"action": "set_secret", "path": "app/key", "value": "secret123"})
    assert result.success is True
    result2 = await ToolRegistry.execute("vault", {"action": "get_secret", "path": "app/key"})
    assert result2.success is True
    # Note: vault is registered as a singleton so state is shared
    assert result2.data["value"] == "secret123"


@pytest.mark.asyncio
async def test_vault_list_secrets():
    result = await ToolRegistry.execute("vault", {"action": "list_secrets", "prefix": ""})
    assert result.success is True
    assert "paths" in result.data


# ── Code Search ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_code_search():
    result = await ToolRegistry.execute(
        "code_search",
        {"action": "search", "query": "authenticate user", "repo": "example/repo", "top_k": 3},
    )
    assert result.success is True
    assert len(result.data["results"]) <= 3


@pytest.mark.asyncio
async def test_code_get_file():
    result = await ToolRegistry.execute(
        "code_search",
        {"action": "get_file", "path": "src/auth.py", "repo": "example/repo"},
    )
    assert result.success is True
    assert "content" in result.data


@pytest.mark.asyncio
async def test_tool_not_found():
    result = await ToolRegistry.execute("nonexistent_tool", {})
    assert result.success is False
    assert "not found" in result.error
