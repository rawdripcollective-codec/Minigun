"""End-to-end tests for the build-feature flow."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from minigun.api.app import create_app
from minigun.config import settings


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.API_SECRET_KEY}"}


def test_health_check_no_auth(client: TestClient) -> None:
    resp = client.get("/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_dashboard_served(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "AI Minigun" in resp.text


def test_post_intent_requires_auth(client: TestClient) -> None:
    resp = client.post("/v1/intents", json={"intent": "build feature", "context": {}})
    assert resp.status_code == 401


def test_post_intent_rejects_invalid_token(client: TestClient) -> None:
    resp = client.post(
        "/v1/intents",
        json={"intent": "build feature", "context": {}},
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert resp.status_code == 403


def test_post_intent_build_feature(client: TestClient, auth_headers: dict) -> None:
    payload = {
        "intent": "build feature: add user authentication",
        "context": {"repo": "minigun", "branch": "feature/auth"},
        "priority": "high",
    }
    resp = client.post("/v1/intents", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert "tasks" in data
    assert len(data["tasks"]) > 0
    assert data["status"] in ("COMPLETED", "FAILED", "PENDING", "RUNNING")


def test_post_intent_deploy_infra(client: TestClient, auth_headers: dict) -> None:
    payload = {
        "intent": "deploy service to kubernetes",
        "context": {"environment": "staging"},
    }
    resp = client.post("/v1/intents", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    solvers = {t["assigned_solver"] for t in data["tasks"]}
    assert "infra" in solvers


def test_graph_task_statuses_are_valid(client: TestClient, auth_headers: dict) -> None:
    payload = {"intent": "implement a code feature", "context": {}}
    resp = client.post("/v1/intents", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    valid_statuses = {"PENDING", "RUNNING", "COMPLETED", "FAILED", "SKIPPED"}
    for task in data["tasks"]:
        assert task["status"] in valid_statuses


def test_post_incident(client: TestClient, auth_headers: dict) -> None:
    payload = {
        "severity": "P1",
        "source": "prometheus",
        "message": "High error rate on api service",
        "metadata": {"service": "api"},
    }
    resp = client.post("/v1/incidents", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "tasks" in data
    assert len(data["tasks"]) > 0


def test_audit_list_returns_list(client: TestClient, auth_headers: dict) -> None:
    resp = client.get("/v1/audit", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
