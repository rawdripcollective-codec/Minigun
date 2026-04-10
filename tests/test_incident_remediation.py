"""End-to-end tests for the incident remediation flow."""

from __future__ import annotations

import pytest

from minigun.execution.incident_engine import IncidentEngine
from minigun.memory.world_model import WorldModelService
from minigun.models.core import IncidentAlert, TaskStatus


@pytest.fixture
def incident_engine() -> IncidentEngine:
    return IncidentEngine()


def _make_alert(**kwargs) -> IncidentAlert:
    defaults = {
        "severity": "P1",
        "source": "prometheus",
        "message": "High error rate detected on api service",
        "metadata": {"service": "api", "threshold": "5%"},
    }
    defaults.update(kwargs)
    return IncidentAlert(**defaults)


def test_ingest_stores_alert(incident_engine: IncidentEngine) -> None:
    alert = _make_alert()
    incident_engine.ingest(alert)
    assert alert.id in incident_engine._alerts


def test_ingest_correlates_alert(incident_engine: IncidentEngine) -> None:
    alert = _make_alert(message="High error rate and cpu spike")
    incident_engine.ingest(alert)
    correlation = incident_engine._correlations[alert.id]
    assert "likely_causes" in correlation
    assert len(correlation["likely_causes"]) > 0


def test_create_remediation_graph_returns_task_graph(incident_engine: IncidentEngine) -> None:
    alert = _make_alert()
    graph = incident_engine.create_remediation_graph(alert)
    assert graph.id
    assert len(graph.tasks) > 0


def test_remediation_graph_contains_sre_tasks(incident_engine: IncidentEngine) -> None:
    alert = _make_alert(message="incident: service is down")
    graph = incident_engine.create_remediation_graph(alert)
    solvers = {t.assigned_solver for t in graph.tasks}
    assert "sre" in solvers


def test_remediation_graph_status_is_pending(incident_engine: IncidentEngine) -> None:
    alert = _make_alert()
    graph = incident_engine.create_remediation_graph(alert)
    # Graph produced by planner (not yet executed) should be PENDING
    assert graph.status == TaskStatus.PENDING


def test_generate_postmortem_returns_dict(incident_engine: IncidentEngine) -> None:
    alert = _make_alert()
    incident_engine.ingest(alert)
    pm = incident_engine.generate_postmortem(alert.id)
    assert pm["incident_id"] == alert.id
    assert "timeline" in pm
    assert "action_items" in pm


def test_generate_postmortem_unknown_id(incident_engine: IncidentEngine) -> None:
    pm = incident_engine.generate_postmortem("nonexistent-id")
    assert "error" in pm


def test_world_model_correlates_cpu_alert() -> None:
    wm = WorldModelService()
    alert = IncidentAlert(severity="P1", source="prometheus", message="cpu usage is very high")
    correlation = wm.correlate_incident(alert)
    assert "resource_exhaustion" in correlation["likely_causes"]


def test_world_model_correlates_latency_alert() -> None:
    wm = WorldModelService()
    alert = IncidentAlert(severity="P2", source="datadog", message="high latency detected")
    correlation = wm.correlate_incident(alert)
    causes = correlation["likely_causes"]
    assert any("latency" in c or "query" in c or "congestion" in c for c in causes)


def test_world_model_update_and_get_state() -> None:
    wm = WorldModelService()
    wm.update("api-service", {"replicas": 3, "status": "degraded"})
    state = wm.get_state("api-service")
    assert state["replicas"] == 3
    assert state["status"] == "degraded"


def test_full_incident_flow() -> None:
    """Full flow: ingest → remediation graph → postmortem."""
    engine = IncidentEngine()
    alert = _make_alert(message="memory leak causing OOM kills in production")
    engine.ingest(alert)
    graph = engine.create_remediation_graph(alert)
    assert len(graph.tasks) > 0
    pm = engine.generate_postmortem(alert.id)
    assert pm["severity"] == alert.severity
    assert "memory_leak" in pm["likely_causes"] or len(pm["likely_causes"]) > 0
