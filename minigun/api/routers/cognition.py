"""Cognition layer router: /api/v1/cognition/*"""

from __future__ import annotations

from fastapi import APIRouter
from typing import Any

from minigun.api.schemas.cognition import (
    PlanRequest, TaskGraphSchema, TaskNodeSchema,
    CritiqueRequest, CritiqueReportSchema,
    MemoryAddRequest, MemorySearchRequest, MemorySearchResult,
    RetrieveRequest, RetrievalResultSchema,
    IntentRequest, IntentSchema,
    UncertaintyRequest, UncertaintyScoreSchema,
    HypothesisRequest, HypothesisSchema,
    PolicyRuleRequest, PolicyEvaluateRequest, PolicyDecisionSchema,
    CausalChainRequest, CausalChainSchema, CausalLinkSchema,
)
from minigun.cognition.planner import TaskPlanner
from minigun.cognition.critic import PlanCritic
from minigun.cognition.memory import MemoryStore
from minigun.cognition.retrieval import RetrievalEngine
from minigun.cognition.intent import IntentInferencer
from minigun.cognition.uncertainty import UncertaintyScorer
from minigun.cognition.hypothesis import HypothesisTester
from minigun.cognition.policy import PolicyEngine, PolicyRule
from minigun.cognition.causal_chain import CausalChainEngine
from minigun.kernel.task_graph import TaskGraph, TaskNode

router = APIRouter(prefix="/api/v1/cognition", tags=["cognition"])

# Singletons
_planner = TaskPlanner()
_critic = PlanCritic()
_memory = MemoryStore()
_retrieval = RetrievalEngine(_memory)
_intent = IntentInferencer()
_uncertainty = UncertaintyScorer()
_hypothesis = HypothesisTester()
_policy = PolicyEngine()
_causal = CausalChainEngine()


def _graph_to_schema(graph: TaskGraph) -> TaskGraphSchema:
    return TaskGraphSchema(
        graph_id=graph.graph_id,
        goal=graph.goal,
        nodes=[
            TaskNodeSchema(
                node_id=n.node_id,
                title=n.title,
                description=n.description,
                tags=n.tags,
                priority=n.priority,
                estimated_tokens=n.estimated_tokens,
                dependencies=n.dependencies,
                metadata=n.metadata,
            )
            for n in graph.nodes()
        ],
    )


def _schema_to_graph(schema: TaskGraphSchema) -> TaskGraph:
    graph = TaskGraph(goal=schema.goal)
    graph.graph_id = schema.graph_id
    for n in schema.nodes:
        graph.add_node(
            TaskNode(
                node_id=n.node_id,
                title=n.title,
                description=n.description,
                tags=n.tags,
                priority=n.priority,
                estimated_tokens=n.estimated_tokens,
                dependencies=n.dependencies,
                metadata=n.metadata,
            )
        )
    return graph


@router.post("/plan", response_model=TaskGraphSchema)
async def plan(req: PlanRequest) -> TaskGraphSchema:
    graph = _planner.decompose(req.goal)
    return _graph_to_schema(graph)


@router.post("/critique", response_model=CritiqueReportSchema)
async def critique(req: CritiqueRequest) -> CritiqueReportSchema:
    graph = _schema_to_graph(req.graph)
    report = _critic.critique(graph)
    return CritiqueReportSchema(
        feasibility=report.feasibility,
        risk=report.risk,
        recommendations=report.recommendations,
        notes=report.notes,
    )


@router.post("/memory")
async def memory_add(req: MemoryAddRequest) -> dict[str, Any]:
    _memory.add(req.key, req.value, req.tags)
    return {"status": "ok", "key": req.key}


@router.get("/memory/{key}")
async def memory_get(key: str) -> dict[str, Any]:
    value = _memory.get(key)
    return {"key": key, "value": value}


@router.get("/memory")
async def memory_list() -> dict[str, Any]:
    return {"keys": _memory.list_keys()}


@router.delete("/memory/{key}")
async def memory_delete(key: str) -> dict[str, Any]:
    deleted = _memory.delete(key)
    return {"key": key, "deleted": deleted}


@router.post("/memory/search", response_model=list[MemorySearchResult])
async def memory_search(req: MemorySearchRequest) -> list[MemorySearchResult]:
    results = _memory.search(req.query, top_k=req.top_k)
    return [MemorySearchResult(**r) for r in results]


@router.post("/retrieve", response_model=list[RetrievalResultSchema])
async def retrieve(req: RetrieveRequest) -> list[RetrievalResultSchema]:
    results = _retrieval.retrieve(req.query, top_k=req.top_k)
    return [
        RetrievalResultSchema(key=r.key, value=r.value, tags=r.tags, score=r.score)
        for r in results
    ]


@router.post("/intent", response_model=IntentSchema)
async def infer_intent(req: IntentRequest) -> IntentSchema:
    intent = _intent.infer(req.goal)
    return IntentSchema(
        intent_type=intent.intent_type,
        confidence=intent.confidence,
        entities=intent.entities,
        raw_goal=intent.raw_goal,
    )


@router.post("/uncertainty", response_model=UncertaintyScoreSchema)
async def score_uncertainty(req: UncertaintyRequest) -> UncertaintyScoreSchema:
    node = TaskNode(
        node_id=req.node.node_id,
        title=req.node.title,
        description=req.node.description,
        tags=req.node.tags,
        priority=req.node.priority,
        estimated_tokens=req.node.estimated_tokens,
        dependencies=req.node.dependencies,
        metadata=req.node.metadata,
    )
    score = _uncertainty.score(node)
    return UncertaintyScoreSchema(
        node_id=score.node_id,
        aleatoric=score.aleatoric,
        epistemic=score.epistemic,
        combined=score.combined,
    )


@router.post("/hypothesis", response_model=list[HypothesisSchema])
async def generate_hypotheses(req: HypothesisRequest) -> list[HypothesisSchema]:
    hyps = _hypothesis.generate(req.observations)
    return [
        HypothesisSchema(
            hypothesis_id=h.hypothesis_id,
            statement=h.statement,
            confidence=h.confidence,
            supporting_observations=h.supporting_observations,
            contradicting_observations=h.contradicting_observations,
        )
        for h in hyps
    ]


@router.post("/policy/rules")
async def add_policy_rule(req: PolicyRuleRequest) -> dict[str, Any]:
    rule = PolicyRule(
        rule_id=req.rule_id,
        action_pattern=req.action_pattern,
        effect=req.effect,
        conditions=req.conditions,
        reason=req.reason,
    )
    _policy.add_rule(rule)
    return {"status": "ok", "rule_id": req.rule_id}


@router.post("/policy/evaluate", response_model=PolicyDecisionSchema)
async def evaluate_policy(req: PolicyEvaluateRequest) -> PolicyDecisionSchema:
    decision = _policy.evaluate(req.action, req.context)
    return PolicyDecisionSchema(
        allowed=decision.allowed,
        reason=decision.reason,
        matched_rule=decision.matched_rule,
    )


@router.post("/causal", response_model=CausalChainSchema)
async def build_causal_chain(req: CausalChainRequest) -> CausalChainSchema:
    chain = _causal.build_chain(req.events)
    return CausalChainSchema(
        chain_id=chain.chain_id,
        events=chain.events,
        links=[
            CausalLinkSchema(
                cause=lnk.cause,
                effect=lnk.effect,
                confidence=lnk.confidence,
                evidence=lnk.evidence,
            )
            for lnk in chain.links
        ],
        summary=chain.summary,
    )
