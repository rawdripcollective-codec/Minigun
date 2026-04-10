"""Tests for the RiskEngine."""

from __future__ import annotations

import pytest

from minigun.execution.risk_engine import RiskEngine
from minigun.models.core import RiskLevel, Task, TaskStatus


@pytest.fixture
def engine() -> RiskEngine:
    return RiskEngine()


def _make_task(name: str = "Test task", task_type: str = "code") -> Task:
    return Task(name=name, type=task_type, status=TaskStatus.COMPLETED, assigned_solver=task_type)


def test_code_task_has_low_base_risk(engine: RiskEngine) -> None:
    task = _make_task(name="Implement changes", task_type="code")
    result = engine.score(task, {"status": "ok"})
    assert result.score < 0.5
    assert result.level in (RiskLevel.LOW, RiskLevel.MEDIUM)


def test_infra_task_has_higher_base_risk(engine: RiskEngine) -> None:
    code_task = _make_task(name="Test task", task_type="code")
    infra_task = _make_task(name="Test task", task_type="infra")
    code_score = engine.score(code_task, {"status": "ok"})
    infra_score = engine.score(infra_task, {"status": "ok"})
    assert infra_score.score > code_score.score


def test_destroy_keyword_increases_risk(engine: RiskEngine) -> None:
    safe_task = _make_task(name="Deploy to staging", task_type="infra")
    risky_task = _make_task(name="Terraform destroy production", task_type="infra")
    safe_score = engine.score(safe_task, {"status": "ok"})
    risky_score = engine.score(risky_task, {"status": "ok"})
    assert risky_score.score > safe_score.score


def test_production_keyword_increases_risk(engine: RiskEngine) -> None:
    dev_task = _make_task(name="Deploy to dev", task_type="infra")
    prod_task = _make_task(name="Deploy to production", task_type="infra")
    dev_score = engine.score(dev_task, {"status": "ok"})
    prod_score = engine.score(prod_task, {"status": "ok"})
    assert prod_score.score > dev_score.score


def test_error_in_result_increases_risk(engine: RiskEngine) -> None:
    task = _make_task(name="Deploy", task_type="infra")
    ok_score = engine.score(task, {"status": "ok"})
    err_score = engine.score(task, {"status": "failed", "error": "timeout"})
    assert err_score.score > ok_score.score


def test_high_risk_requires_approval(engine: RiskEngine) -> None:
    task = _make_task(name="Terraform destroy production cluster", task_type="infra")
    result = engine.score(task, {"status": "ok"})
    if result.score >= 0.7:
        assert result.requires_approval is True


def test_low_risk_does_not_require_approval(engine: RiskEngine) -> None:
    task = _make_task(name="Analyse codebase", task_type="code")
    result = engine.score(task, {"status": "ok"})
    assert result.requires_approval is False


def test_risk_score_bounded(engine: RiskEngine) -> None:
    task = _make_task(name="Destroy production delete drop data", task_type="sre")
    result = engine.score(task, {"status": "failed", "error": "catastrophic failure"})
    assert 0.0 <= result.score <= 1.0


def test_risk_factors_list_populated(engine: RiskEngine) -> None:
    task = _make_task(name="Deploy to production", task_type="infra")
    result = engine.score(task, {"status": "ok"})
    assert len(result.factors) > 0


def test_sre_task_has_higher_risk_than_code(engine: RiskEngine) -> None:
    code_task = _make_task(name="Implement feature", task_type="code")
    sre_task = _make_task(name="Apply remediation", task_type="sre")
    code_score = engine.score(code_task, {"status": "ok"})
    sre_score = engine.score(sre_task, {"status": "ok"})
    assert sre_score.score > code_score.score
