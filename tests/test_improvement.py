"""Tests for the self-improvement layer."""

import pytest
from minigun.improvement.evaluation import OfflineEvaluator
from minigun.improvement.telemetry import TelemetryCollector
from minigun.improvement.dataset import DatasetMiner
from minigun.improvement.reward import RewardModel
from minigun.improvement.synthetic import SyntheticTaskGenerator
from minigun.improvement.refresh import ModelRefreshController, RefreshStatus


# ── Evaluator ─────────────────────────────────────────────────────────────

def test_evaluator_success():
    evaluator = OfflineEvaluator()
    result = evaluator.evaluate({"success": True, "steps_completed": 5, "steps_total": 5})
    assert result.score > 0.5
    assert "correctness" in result.breakdown


def test_evaluator_failure():
    evaluator = OfflineEvaluator()
    result = evaluator.evaluate({"success": False, "steps_completed": 0, "steps_total": 3})
    assert result.score < 0.5


def test_evaluator_partial():
    evaluator = OfflineEvaluator()
    result = evaluator.evaluate({"success": True, "steps_completed": 3, "steps_total": 5})
    assert 0.0 <= result.score <= 1.0
    assert len(result.notes) > 0


# ── Telemetry ──────────────────────────────────────────────────────────────

def test_telemetry_record_and_flush():
    collector = TelemetryCollector()
    e1 = collector.record_event("agent.run", {"goal": "test"})
    e2 = collector.record_event("agent.run", {"goal": "test2"})
    flushed = collector.flush()
    assert len(flushed) == 2
    assert collector.flush() == []  # already flushed


def test_telemetry_summary():
    collector = TelemetryCollector()
    collector.record_event("event_a", {})
    collector.record_event("event_a", {})
    collector.record_event("event_b", {})
    summary = collector.summary()
    assert summary["total_events"] == 3
    assert summary["event_counts"]["event_a"] == 2


# ── DatasetMiner ───────────────────────────────────────────────────────────

def test_dataset_mine_basic():
    miner = DatasetMiner()
    ds = miner.mine("github://example/repo", {"limit": 5, "domain": "codegen"})
    assert ds.total == 5
    assert len(ds.examples) == 5
    assert ds.source == "github://example/repo"


def test_dataset_mine_default_limit():
    miner = DatasetMiner()
    ds = miner.mine("local://data")
    assert ds.total == 10


def test_dataset_examples_have_tags():
    miner = DatasetMiner()
    ds = miner.mine("s3://bucket/data", {"limit": 3})
    for example in ds.examples:
        assert len(example.tags) > 0


# ── RewardModel ────────────────────────────────────────────────────────────

def test_reward_all_success():
    model = RewardModel()
    trajectory = [{"success": True} for _ in range(5)]
    score = model.score(trajectory)
    assert score > 0.5


def test_reward_all_failure():
    model = RewardModel()
    trajectory = [{"success": False, "error": "oops"} for _ in range(5)]
    score = model.score(trajectory)
    assert score >= 0.0


def test_reward_empty():
    model = RewardModel()
    assert model.score([]) == 0.0


def test_reward_mixed():
    model = RewardModel()
    trajectory = [
        {"success": True},
        {"success": False, "error": "timeout"},
        {"success": True, "retries": 2},
    ]
    score = model.score(trajectory)
    assert 0.0 <= score <= 1.0


# ── SyntheticTaskGenerator ─────────────────────────────────────────────────

def test_synthetic_generate():
    gen = SyntheticTaskGenerator()
    tasks = gen.generate("codegen", 5)
    assert len(tasks) == 5
    assert all(t.domain == "codegen" for t in tasks)


def test_synthetic_difficulty_variety():
    gen = SyntheticTaskGenerator()
    tasks = gen.generate("devops", 9)
    difficulties = {t.difficulty for t in tasks}
    assert len(difficulties) > 1


def test_synthetic_unknown_domain():
    gen = SyntheticTaskGenerator()
    tasks = gen.generate("unknown_domain", 3)
    assert len(tasks) == 3  # falls back to codegen template


# ── ModelRefreshController ─────────────────────────────────────────────────

def test_refresh_schedule():
    ctrl = ModelRefreshController()
    job = ctrl.schedule_refresh("model-v1", "dataset-001", {"epochs": 3})
    assert job.refresh_id is not None
    assert job.status == RefreshStatus.SCHEDULED


def test_refresh_status():
    ctrl = ModelRefreshController()
    job = ctrl.schedule_refresh("model-v2", "ds-002")
    retrieved = ctrl.status(job.refresh_id)
    assert retrieved is not None
    assert retrieved.refresh_id == job.refresh_id


def test_refresh_cancel():
    ctrl = ModelRefreshController()
    job = ctrl.schedule_refresh("model-v3", "ds-003")
    assert ctrl.cancel(job.refresh_id) is True
    assert ctrl.status(job.refresh_id).status == RefreshStatus.CANCELLED


def test_refresh_cancel_nonexistent():
    ctrl = ModelRefreshController()
    assert ctrl.cancel("nonexistent") is False


def test_refresh_list_jobs():
    ctrl = ModelRefreshController()
    ctrl.schedule_refresh("m1", "d1")
    ctrl.schedule_refresh("m2", "d2")
    assert len(ctrl.list_jobs()) >= 2
