"""Tests for the kernel layer."""

import pytest
from minigun.kernel.task_graph import TaskGraph, TaskNode, CycleError
from minigun.kernel.agent import AgentKernel
from minigun.kernel.executor import SpecialisedExecutor
import minigun.tools.mcp  # noqa: F401


# ── TaskGraph ──────────────────────────────────────────────────────────────

def test_task_graph_add_and_get():
    graph = TaskGraph(goal="test goal")
    node = TaskNode(title="Step 1", tags=["testing"])
    graph.add_node(node)
    assert graph.get_node(node.node_id) is not None
    assert len(graph) == 1


def test_task_graph_topological_sort_linear():
    graph = TaskGraph(goal="linear")
    n1 = TaskNode(title="A")
    n2 = TaskNode(title="B", dependencies=[n1.node_id])
    n3 = TaskNode(title="C", dependencies=[n2.node_id])
    for n in [n1, n2, n3]:
        graph.add_node(n)
    order = graph.topological_sort()
    titles = [n.title for n in order]
    assert titles.index("A") < titles.index("B") < titles.index("C")


def test_task_graph_no_cycle():
    graph = TaskGraph()
    n1 = TaskNode(title="X")
    n2 = TaskNode(title="Y", dependencies=[n1.node_id])
    graph.add_node(n1)
    graph.add_node(n2)
    assert graph.has_cycle() is False


def test_task_graph_cycle_detection():
    graph = TaskGraph()
    n1 = TaskNode(node_id="a", title="A")
    n2 = TaskNode(node_id="b", title="B", dependencies=["a"])
    n1.dependencies = ["b"]  # create cycle: a → b → a
    graph.add_node(n1)
    graph.add_node(n2)
    assert graph.has_cycle() is True


def test_task_graph_cycle_raises_on_sort():
    graph = TaskGraph()
    n1 = TaskNode(node_id="x", title="X")
    n2 = TaskNode(node_id="y", title="Y", dependencies=["x"])
    n1.dependencies = ["y"]
    graph.add_node(n1)
    graph.add_node(n2)
    with pytest.raises(CycleError):
        graph.topological_sort()


def test_task_graph_remove_node():
    graph = TaskGraph()
    n = TaskNode(title="Remove me")
    graph.add_node(n)
    graph.remove_node(n.node_id)
    assert graph.get_node(n.node_id) is None


def test_task_graph_empty_sort():
    graph = TaskGraph()
    assert graph.topological_sort() == []


# ── AgentKernel ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_agent_kernel_run():
    kernel = AgentKernel()
    result = await kernel.run("Build and deploy a Python microservice")
    assert result.run_id is not None
    assert result.goal == "Build and deploy a Python microservice"
    assert result.success is True
    assert result.steps_completed > 0
    assert 0.0 <= result.plan_feasibility <= 1.0
    assert 0.0 <= result.plan_risk <= 1.0
    assert result.critique_iterations >= 1


@pytest.mark.asyncio
async def test_agent_kernel_intent():
    kernel = AgentKernel()
    result = await kernel.run("Write unit tests for the auth module")
    assert result.intent_type == "testing"


@pytest.mark.asyncio
async def test_agent_kernel_telemetry():
    kernel = AgentKernel()
    result = await kernel.run("Generate API documentation")
    assert result.telemetry_summary["total_events"] > 0


# ── SpecialisedExecutor ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_executor_codegen_node():
    executor = SpecialisedExecutor()
    node = TaskNode(title="Generate code", tags=["codegen"])
    result = await executor.execute(node)
    assert "app" in result or "status" in result


@pytest.mark.asyncio
async def test_executor_generic_node():
    executor = SpecialisedExecutor()
    node = TaskNode(title="Some task", tags=["general"])
    result = await executor.execute(node)
    assert result["node_id"] == node.node_id


@pytest.mark.asyncio
async def test_executor_cloud_node():
    executor = SpecialisedExecutor()
    node = TaskNode(title="Deploy", tags=["deployment"])
    result = await executor.execute(node)
    assert "tool" in result or "app" in result


@pytest.mark.asyncio
async def test_executor_testing_node():
    executor = SpecialisedExecutor()
    node = TaskNode(title="Write tests", tags=["testing"])
    result = await executor.execute(node)
    assert "app" in result
