"""Tests for PlannerAgent."""

from __future__ import annotations

import pytest

from minigun.agents.planner import PlannerAgent
from minigun.models.core import IntentRequest, TaskStatus


@pytest.fixture
def planner() -> PlannerAgent:
    return PlannerAgent()


def test_plan_code_intent_returns_task_graph(planner: PlannerAgent) -> None:
    req = IntentRequest(intent="build this feature: user authentication", context={})
    graph = planner.plan(req)
    assert graph.intent == req.intent
    assert len(graph.tasks) > 0
    assert graph.status == TaskStatus.PENDING


def test_plan_assigns_correct_solver_for_code(planner: PlannerAgent) -> None:
    req = IntentRequest(intent="implement a new feature", context={})
    graph = planner.plan(req)
    solvers = {t.assigned_solver for t in graph.tasks}
    assert "code" in solvers


def test_plan_assigns_correct_solver_for_infra(planner: PlannerAgent) -> None:
    req = IntentRequest(intent="deploy to kubernetes cluster", context={})
    graph = planner.plan(req)
    solvers = {t.assigned_solver for t in graph.tasks}
    assert "infra" in solvers


def test_plan_assigns_correct_solver_for_sre(planner: PlannerAgent) -> None:
    req = IntentRequest(intent="remediate incident: high error rate", context={})
    graph = planner.plan(req)
    solvers = {t.assigned_solver for t in graph.tasks}
    assert "sre" in solvers


def test_plan_assigns_correct_solver_for_data(planner: PlannerAgent) -> None:
    req = IntentRequest(intent="run analytics data pipeline", context={})
    graph = planner.plan(req)
    solvers = {t.assigned_solver for t in graph.tasks}
    assert "data" in solvers


def test_plan_builds_dependency_chain(planner: PlannerAgent) -> None:
    req = IntentRequest(intent="implement new feature", context={})
    graph = planner.plan(req)
    # Each task beyond the first should have exactly one dependency
    for task in graph.tasks[1:]:
        assert len(task.dependencies) == 1


def test_plan_edges_match_dependency_chain(planner: PlannerAgent) -> None:
    req = IntentRequest(intent="build feature", context={})
    graph = planner.plan(req)
    assert len(graph.edges) == len(graph.tasks) - 1


def test_plan_tasks_have_unique_ids(planner: PlannerAgent) -> None:
    req = IntentRequest(intent="build feature", context={})
    graph = planner.plan(req)
    ids = [t.id for t in graph.tasks]
    assert len(ids) == len(set(ids))


def test_plan_task_inputs_contain_intent(planner: PlannerAgent) -> None:
    req = IntentRequest(intent="implement oauth feature", context={"repo": "my-repo"})
    graph = planner.plan(req)
    for task in graph.tasks:
        assert task.inputs["intent"] == req.intent


def test_plan_unknown_intent_defaults_to_code(planner: PlannerAgent) -> None:
    req = IntentRequest(intent="do something unrecognised", context={})
    graph = planner.plan(req)
    solvers = {t.assigned_solver for t in graph.tasks}
    assert "code" in solvers
