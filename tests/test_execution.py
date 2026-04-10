"""Tests for the execution layer."""

import pytest
from minigun.execution.workflow import WorkflowEngine, StepStatus
from minigun.execution.queue import JobQueue, JobStatus
from minigun.execution.sandbox import SandboxRunner
from minigun.execution.permissions import PermissionManager
from minigun.execution.rollback import RollbackManager
from minigun.execution.audit import AuditLogger
from minigun.execution.approval import ApprovalGate, ApprovalStatus
from minigun.cognition.planner import TaskPlanner


# ── Workflow ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_workflow_create_and_run():
    planner = TaskPlanner()
    engine = WorkflowEngine()
    graph = planner.decompose("Write a Python script")
    wf = engine.create_workflow(graph)
    assert wf.workflow_id is not None
    assert len(wf.steps) > 0

    result = await engine.run(wf.workflow_id)
    assert result.success is True
    assert result.steps_completed > 0
    assert result.steps_failed == 0


@pytest.mark.asyncio
async def test_workflow_not_found():
    engine = WorkflowEngine()
    result = await engine.run("nonexistent-id")
    assert result.success is False
    assert result.error is not None


def test_workflow_get():
    planner = TaskPlanner()
    engine = WorkflowEngine()
    graph = planner.decompose("Test workflow")
    wf = engine.create_workflow(graph)
    retrieved = engine.get_workflow(wf.workflow_id)
    assert retrieved is not None
    assert retrieved.workflow_id == wf.workflow_id


# ── Queue ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_queue_enqueue_dequeue():
    queue = JobQueue()
    job_id = await queue.enqueue({"task": "example"})
    assert job_id is not None

    job = await queue.dequeue()
    assert job is not None
    assert job.job_id == job_id


@pytest.mark.asyncio
async def test_queue_status():
    queue = JobQueue()
    job_id = await queue.enqueue({"type": "build"})
    status = queue.status(job_id)
    assert status == JobStatus.QUEUED


@pytest.mark.asyncio
async def test_queue_list_jobs():
    queue = JobQueue()
    await queue.enqueue({"a": 1})
    await queue.enqueue({"b": 2})
    jobs = queue.list_jobs()
    assert len(jobs) >= 2


@pytest.mark.asyncio
async def test_queue_dequeue_empty():
    queue = JobQueue()
    job = await queue.dequeue()
    assert job is None


# ── Sandbox ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_sandbox_python_success():
    sandbox = SandboxRunner()
    result = await sandbox.run_code("python", "print('hello')")
    assert result.success is True
    assert "hello" in result.stdout


@pytest.mark.asyncio
async def test_sandbox_python_error():
    sandbox = SandboxRunner()
    result = await sandbox.run_code("python", "raise ValueError('test error')")
    assert result.success is False


@pytest.mark.asyncio
async def test_sandbox_simulated_language():
    sandbox = SandboxRunner()
    result = await sandbox.run_code("javascript", "console.log('hi')", timeout_s=5.0)
    assert result.success is True
    assert "simulated" in result.stdout


# ── Permissions ────────────────────────────────────────────────────────────

def test_permissions_grant_and_check():
    pm = PermissionManager()
    pm.grant("alice", "docs", "read")
    assert pm.check("alice", "docs", "read") is True
    assert pm.check("alice", "docs", "write") is False


def test_permissions_revoke():
    pm = PermissionManager()
    pm.grant("bob", "repo", "push")
    pm.revoke("bob", "repo", "push")
    assert pm.check("bob", "repo", "push") is False


def test_permissions_wildcard():
    pm = PermissionManager()
    pm.grant("admin", "*", "*")
    assert pm.check("admin", "anything", "delete") is True


def test_permissions_list_grants():
    pm = PermissionManager()
    pm.grant("u1", "r1", "read")
    grants = pm.list_grants()
    assert any(g["principal"] == "u1" for g in grants)


# ── Rollback ───────────────────────────────────────────────────────────────

def test_rollback_checkpoint_and_restore():
    rm = RollbackManager()
    state = {"version": 1, "config": {"debug": True}}
    rm.checkpoint("v1", state)
    restored = rm.rollback_to("v1")
    assert restored == state
    # Ensure deep copy
    restored["version"] = 99
    assert rm.rollback_to("v1")["version"] == 1


def test_rollback_missing_label():
    rm = RollbackManager()
    assert rm.rollback_to("nonexistent") is None


def test_rollback_list():
    rm = RollbackManager()
    rm.checkpoint("a", {})
    rm.checkpoint("b", {})
    assert rm.list_checkpoints() == ["a", "b"]


# ── Audit ──────────────────────────────────────────────────────────────────

def test_audit_record_and_query():
    logger = AuditLogger()
    entry = logger.record("alice", "deploy", "service-a", "success")
    assert entry.entry_id is not None
    entries = logger.query()
    assert any(e.entry_id == entry.entry_id for e in entries)


def test_audit_query_with_filter():
    logger = AuditLogger()
    logger.record("alice", "read", "docs", "success")
    logger.record("bob", "write", "repo", "success")
    results = logger.query({"actor": "alice"})
    assert all(e.actor == "alice" for e in results)


# ── Approval ───────────────────────────────────────────────────────────────

def test_approval_request_and_approve():
    gate = ApprovalGate()
    ticket = gate.request_approval({"action": "deploy", "env": "prod"})
    assert ticket.status == ApprovalStatus.PENDING

    approved = gate.approve(ticket.ticket_id, "manager")
    assert approved.status == ApprovalStatus.APPROVED
    assert approved.approver == "manager"


def test_approval_reject():
    gate = ApprovalGate()
    ticket = gate.request_approval({"action": "delete"})
    rejected = gate.reject(ticket.ticket_id, "manager", reason="Too risky")
    assert rejected.status == ApprovalStatus.REJECTED
    assert rejected.rejection_reason == "Too risky"


def test_approval_status():
    gate = ApprovalGate()
    ticket = gate.request_approval({"x": 1})
    assert gate.status(ticket.ticket_id) == ApprovalStatus.PENDING
    assert gate.status("nonexistent") is None
