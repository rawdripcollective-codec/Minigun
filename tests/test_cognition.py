"""Tests for the cognition layer."""

import pytest
from minigun.cognition.planner import TaskPlanner
from minigun.cognition.critic import PlanCritic
from minigun.cognition.memory import MemoryStore
from minigun.cognition.retrieval import RetrievalEngine
from minigun.cognition.uncertainty import UncertaintyScorer
from minigun.cognition.policy import PolicyEngine, PolicyRule
from minigun.cognition.intent import IntentInferencer
from minigun.cognition.hypothesis import HypothesisTester
from minigun.cognition.causal_chain import CausalChainEngine
from minigun.kernel.task_graph import TaskNode, TaskGraph


# ── Planner ────────────────────────────────────────────────────────────────

def test_planner_returns_task_graph():
    planner = TaskPlanner()
    graph = planner.decompose("Build a REST API in Python")
    assert len(graph) > 0
    assert graph.goal == "Build a REST API in Python"


def test_planner_nodes_have_dependencies():
    planner = TaskPlanner()
    graph = planner.decompose("Deploy to AWS")
    nodes = graph.nodes()
    # All nodes except the first should have at least one dependency
    dep_nodes = [n for n in nodes if n.dependencies]
    assert len(dep_nodes) > 0


def test_planner_topological_sort():
    planner = TaskPlanner()
    graph = planner.decompose("Refactor authentication module")
    order = graph.topological_sort()
    assert len(order) == len(graph.nodes())


# ── Critic ─────────────────────────────────────────────────────────────────

def test_critic_empty_graph():
    critic = PlanCritic()
    graph = TaskGraph(goal="")
    report = critic.critique(graph)
    assert report.feasibility == 0.0
    assert report.risk == 1.0
    assert len(report.recommendations) > 0


def test_critic_normal_graph():
    planner = TaskPlanner()
    critic = PlanCritic()
    graph = planner.decompose("Write unit tests")
    report = critic.critique(graph)
    assert 0.0 <= report.feasibility <= 1.0
    assert 0.0 <= report.risk <= 1.0
    assert len(report.recommendations) > 0


def test_critic_high_risk_graph():
    critic = PlanCritic()
    graph = TaskGraph(goal="deploy to cloud")
    node = TaskNode(title="Deploy", tags=["deployment", "cloud", "security", "database"])
    graph.add_node(node)
    report = critic.critique(graph)
    assert report.risk > 0.0


# ── Memory ─────────────────────────────────────────────────────────────────

def test_memory_add_and_get():
    store = MemoryStore()
    store.add("key1", "value1", tags=["test"])
    assert store.get("key1") == "value1"


def test_memory_list_keys():
    store = MemoryStore()
    store.add("a", 1)
    store.add("b", 2)
    assert set(["a", "b"]).issubset(set(store.list_keys()))


def test_memory_search():
    store = MemoryStore()
    store.add("python_tutorial", "Learn Python basics", tags=["python", "tutorial"])
    store.add("go_guide", "Go programming guide", tags=["go"])
    results = store.search("python tutorial")
    assert len(results) > 0
    assert results[0]["key"] == "python_tutorial"


def test_memory_delete():
    store = MemoryStore()
    store.add("temp", "data")
    assert store.delete("temp") is True
    assert store.get("temp") is None
    assert store.delete("temp") is False


# ── Retrieval ──────────────────────────────────────────────────────────────

def test_retrieval_engine():
    store = MemoryStore()
    store.add("docs", "documentation for API", tags=["api", "docs"])
    engine = RetrievalEngine(store)
    results = engine.retrieve("API documentation")
    assert len(results) > 0
    assert results[0].key == "docs"


# ── Uncertainty ────────────────────────────────────────────────────────────

def test_uncertainty_scorer_basic():
    scorer = UncertaintyScorer()
    node = TaskNode(title="Deploy service", tags=["deployment", "cloud"], estimated_tokens=2000)
    score = scorer.score(node)
    assert 0.0 <= score.aleatoric <= 1.0
    assert 0.0 <= score.epistemic <= 1.0
    assert 0.0 <= score.combined <= 1.0
    assert score.node_id == node.node_id


def test_uncertainty_scorer_low_risk():
    scorer = UncertaintyScorer()
    node = TaskNode(title="Write docs", tags=["documentation"], estimated_tokens=200)
    score = scorer.score(node)
    assert score.combined < 0.8


# ── Policy ─────────────────────────────────────────────────────────────────

def test_policy_default_allow():
    engine = PolicyEngine()
    decision = engine.evaluate("read:data")
    assert decision.allowed is True


def test_policy_deny_rule():
    engine = PolicyEngine()
    engine.add_rule(PolicyRule(
        rule_id="r1",
        action_pattern="delete:*",
        effect="deny",
        reason="Deletions not allowed",
    ))
    decision = engine.evaluate("delete:users")
    assert decision.allowed is False
    assert decision.matched_rule == "r1"


def test_policy_allow_rule():
    engine = PolicyEngine()
    engine._default_effect = "deny"
    engine.add_rule(PolicyRule(
        rule_id="r2",
        action_pattern="read:*",
        effect="allow",
    ))
    decision = engine.evaluate("read:documents")
    assert decision.allowed is True


def test_policy_wildcard():
    engine = PolicyEngine()
    engine.add_rule(PolicyRule(
        rule_id="r3",
        action_pattern="deploy:prod*",
        effect="deny",
    ))
    assert engine.evaluate("deploy:production").allowed is False
    assert engine.evaluate("deploy:staging").allowed is True


# ── Intent ─────────────────────────────────────────────────────────────────

def test_intent_codegen():
    inferencer = IntentInferencer()
    intent = inferencer.infer("Generate a Python class for user authentication")
    assert intent.intent_type in {"codegen", "security", "general"}
    assert 0.0 <= intent.confidence <= 1.0


def test_intent_testing():
    inferencer = IntentInferencer()
    intent = inferencer.infer("Write tests for the login module")
    assert intent.intent_type == "testing"


def test_intent_entities():
    inferencer = IntentInferencer()
    intent = inferencer.infer("Deploy the UserService to AWS using Python")
    # Should detect language entity
    lang_entities = [e for e in intent.entities if e["type"] == "language"]
    assert any(e["value"] == "Python" for e in lang_entities)


# ── Hypothesis ─────────────────────────────────────────────────────────────

def test_hypothesis_generation():
    tester = HypothesisTester()
    hypotheses = tester.generate(["error: connection timeout", "network unreachable"])
    assert len(hypotheses) > 0
    # Results should be sorted by confidence descending
    confidences = [h.confidence for h in hypotheses]
    assert confidences == sorted(confidences, reverse=True)


def test_hypothesis_empty_observations():
    tester = HypothesisTester()
    hypotheses = tester.generate([])
    assert len(hypotheses) > 0  # templates still generated with low confidence


# ── Causal Chain ───────────────────────────────────────────────────────────

def test_causal_chain_basic():
    engine = CausalChainEngine()
    events = ["deploy started", "health check failed", "rollback triggered"]
    chain = engine.build_chain(events)
    assert len(chain.links) == 2
    assert chain.links[0].cause == "deploy started"
    assert chain.links[0].effect == "health check failed"


def test_causal_chain_empty():
    engine = CausalChainEngine()
    chain = engine.build_chain([])
    assert chain.links == []
    assert "No events" in chain.summary


def test_causal_chain_single_event():
    engine = CausalChainEngine()
    chain = engine.build_chain(["event one"])
    assert chain.links == []
