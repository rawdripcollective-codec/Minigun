"""Tests for the REST API layer."""

import pytest
from httpx import AsyncClient, ASGITransport
from minigun.api.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ── Health ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── Cognition ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_plan(client):
    resp = await client.post("/api/v1/cognition/plan", json={"goal": "Build a REST API"})
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert len(data["nodes"]) > 0


@pytest.mark.asyncio
async def test_api_critique(client):
    # First get a plan
    plan_resp = await client.post("/api/v1/cognition/plan", json={"goal": "Deploy service"})
    graph = plan_resp.json()
    resp = await client.post("/api/v1/cognition/critique", json={"graph": graph})
    assert resp.status_code == 200
    data = resp.json()
    assert "feasibility" in data
    assert "risk" in data


@pytest.mark.asyncio
async def test_api_memory_crud(client):
    # Add
    resp = await client.post("/api/v1/cognition/memory", json={"key": "k1", "value": "v1", "tags": ["t1"]})
    assert resp.status_code == 200

    # Get
    resp = await client.get("/api/v1/cognition/memory/k1")
    assert resp.json()["value"] == "v1"

    # List
    resp = await client.get("/api/v1/cognition/memory")
    assert "k1" in resp.json()["keys"]

    # Delete
    resp = await client.delete("/api/v1/cognition/memory/k1")
    assert resp.json()["deleted"] is True


@pytest.mark.asyncio
async def test_api_memory_search(client):
    await client.post("/api/v1/cognition/memory", json={"key": "py_docs", "value": "Python documentation", "tags": ["python"]})
    resp = await client.post("/api/v1/cognition/memory/search", json={"query": "Python", "top_k": 3})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_api_retrieve(client):
    resp = await client.post("/api/v1/cognition/retrieve", json={"query": "test", "top_k": 3})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_api_intent(client):
    resp = await client.post("/api/v1/cognition/intent", json={"goal": "Write unit tests for auth module"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent_type"] == "testing"


@pytest.mark.asyncio
async def test_api_uncertainty(client):
    node = {
        "node_id": "test-node",
        "title": "Deploy to cloud",
        "description": "Deploy the service",
        "tags": ["deployment", "cloud"],
        "priority": 3,
        "estimated_tokens": 1500,
        "dependencies": [],
        "metadata": {},
    }
    resp = await client.post("/api/v1/cognition/uncertainty", json={"node": node})
    assert resp.status_code == 200
    data = resp.json()
    assert "combined" in data


@pytest.mark.asyncio
async def test_api_hypothesis(client):
    resp = await client.post(
        "/api/v1/cognition/hypothesis",
        json={"observations": ["error: connection timeout", "network unreachable"]},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_api_policy(client):
    await client.post(
        "/api/v1/cognition/policy/rules",
        json={"rule_id": "r1", "action_pattern": "delete:*", "effect": "deny", "conditions": {}, "reason": ""},
    )
    resp = await client.post("/api/v1/cognition/policy/evaluate", json={"action": "delete:users", "context": {}})
    assert resp.status_code == 200
    assert resp.json()["allowed"] is False


@pytest.mark.asyncio
async def test_api_causal(client):
    resp = await client.post(
        "/api/v1/cognition/causal",
        json={"events": ["deploy started", "health check failed", "rollback triggered"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["links"]) == 2


# ── Tools ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_tools_list(client):
    resp = await client.get("/api/v1/tools/")
    assert resp.status_code == 200
    names = {t["name"] for t in resp.json()}
    assert "browser" in names


@pytest.mark.asyncio
async def test_api_tools_execute(client):
    resp = await client.post(
        "/api/v1/tools/execute",
        json={"name": "git", "params": {"action": "status"}},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ── Execution ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_workflow(client):
    resp = await client.post("/api/v1/execution/workflows", json={"goal": "Deploy app"})
    assert resp.status_code == 200
    wf_id = resp.json()["workflow_id"]

    run_resp = await client.post(f"/api/v1/execution/workflows/{wf_id}/run")
    assert run_resp.status_code == 200
    assert run_resp.json()["success"] is True


@pytest.mark.asyncio
async def test_api_jobs(client):
    resp = await client.post("/api/v1/execution/jobs", json={"payload": {"task": "build"}})
    assert resp.status_code == 200
    job_id = resp.json()["job_id"]

    status_resp = await client.get(f"/api/v1/execution/jobs/{job_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["job_id"] == job_id


@pytest.mark.asyncio
async def test_api_sandbox(client):
    resp = await client.post(
        "/api/v1/execution/sandbox",
        json={"language": "python", "code": "print('hello world')", "timeout_s": 10},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "hello world" in data["stdout"]


@pytest.mark.asyncio
async def test_api_permissions(client):
    await client.post("/api/v1/execution/permissions/grant", json={"principal": "alice", "resource": "docs", "action": "read"})
    check = await client.post("/api/v1/execution/permissions/check", json={"principal": "alice", "resource": "docs", "action": "read"})
    assert check.json()["allowed"] is True


@pytest.mark.asyncio
async def test_api_rollback(client):
    await client.post("/api/v1/execution/rollback/checkpoint", json={"label": "v1", "state": {"x": 1}})
    resp = await client.post("/api/v1/execution/rollback/restore", json={"label": "v1"})
    assert resp.status_code == 200
    assert resp.json()["state"]["x"] == 1


@pytest.mark.asyncio
async def test_api_audit(client):
    await client.post("/api/v1/execution/audit", json={"actor": "alice", "action": "deploy", "resource": "app", "outcome": "success", "metadata": {}})
    resp = await client.get("/api/v1/execution/audit")
    assert resp.status_code == 200
    entries = resp.json()
    assert any(e["actor"] == "alice" for e in entries)


@pytest.mark.asyncio
async def test_api_approvals(client):
    resp = await client.post("/api/v1/execution/approvals", json={"request": {"action": "deploy"}})
    assert resp.status_code == 200
    ticket_id = resp.json()["ticket_id"]

    approve_resp = await client.post(
        f"/api/v1/execution/approvals/{ticket_id}/approve",
        json={"approver": "manager"},
    )
    assert approve_resp.json()["status"] == "approved"


# ── Apps ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_codegen(client):
    resp = await client.post(
        "/api/v1/apps/codegen",
        json={"language": "python", "description": "sort a list of items"},
    )
    assert resp.status_code == 200
    assert "class" in resp.json()["code"].lower() or "def" in resp.json()["code"].lower()


@pytest.mark.asyncio
async def test_api_pr_review(client):
    resp = await client.post(
        "/api/v1/apps/pr-review",
        json={"diff": "--- a/main.py\n+++ b/main.py\n+print('debug')", "context": ""},
    )
    assert resp.status_code == 200
    assert "risk_level" in resp.json()


@pytest.mark.asyncio
async def test_api_testing(client):
    resp = await client.post(
        "/api/v1/apps/testing",
        json={"code": "def add(a, b): return a + b", "language": "python"},
    )
    assert resp.status_code == 200
    assert resp.json()["framework"] == "pytest"


@pytest.mark.asyncio
async def test_api_architecture(client):
    resp = await client.post(
        "/api/v1/apps/architecture",
        json={"requirements": "Build a REST API with database and authentication"},
    )
    assert resp.status_code == 200
    assert len(resp.json()["components"]) > 0


@pytest.mark.asyncio
async def test_api_support(client):
    resp = await client.post("/api/v1/apps/support", json={"ticket": "App crashes with fatal exception"})
    assert resp.status_code == 200
    assert resp.json()["priority"] == "critical"


@pytest.mark.asyncio
async def test_api_compliance(client):
    resp = await client.post(
        "/api/v1/apps/compliance",
        json={"artifact": "def safe(): return 1", "standards": ["OWASP"]},
    )
    assert resp.status_code == 200
    assert "overall_status" in resp.json()


@pytest.mark.asyncio
async def test_api_workflow_automation(client):
    resp = await client.post(
        "/api/v1/apps/workflow-automation",
        json={"trigger": {"event": "push"}, "steps": [{"name": "build"}, {"name": "test"}]},
    )
    assert resp.status_code == 200
    auto_id = resp.json()["automation_id"]

    run_resp = await client.post(f"/api/v1/apps/workflow-automation/{auto_id}/run")
    assert run_resp.status_code == 200
    assert run_resp.json()["steps_executed"] == 2


# ── Improvement ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_evaluate(client):
    resp = await client.post(
        "/api/v1/improvement/evaluate",
        json={"task_run": {"success": True, "steps_completed": 5, "steps_total": 5}},
    )
    assert resp.status_code == 200
    assert resp.json()["score"] > 0.5


@pytest.mark.asyncio
async def test_api_telemetry(client):
    await client.post("/api/v1/improvement/telemetry/event", json={"name": "test.event", "data": {"x": 1}})
    resp = await client.get("/api/v1/improvement/telemetry/summary")
    assert resp.status_code == 200
    assert resp.json()["total_events"] >= 1


@pytest.mark.asyncio
async def test_api_dataset(client):
    resp = await client.post(
        "/api/v1/improvement/dataset/mine",
        json={"source": "github://test/repo", "filters": {"limit": 3}},
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 3


@pytest.mark.asyncio
async def test_api_reward(client):
    resp = await client.post(
        "/api/v1/improvement/reward/score",
        json={"trajectory": [{"success": True}, {"success": True}]},
    )
    assert resp.status_code == 200
    assert resp.json()["score"] > 0


@pytest.mark.asyncio
async def test_api_synthetic(client):
    resp = await client.post(
        "/api/v1/improvement/synthetic/generate",
        json={"domain": "codegen", "n": 3},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 3


@pytest.mark.asyncio
async def test_api_refresh(client):
    resp = await client.post(
        "/api/v1/improvement/refresh/schedule",
        json={"model_id": "model-v1", "dataset_id": "ds-001", "params": {}},
    )
    assert resp.status_code == 200
    refresh_id = resp.json()["refresh_id"]

    status_resp = await client.get(f"/api/v1/improvement/refresh/{refresh_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "scheduled"


# ── Kernel ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_kernel_run(client):
    resp = await client.post("/api/v1/kernel/run", json={"goal": "Build and test a Python service"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["steps_completed"] > 0
    assert "run_id" in data
