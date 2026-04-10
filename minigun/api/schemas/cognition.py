"""Pydantic schemas for the Cognition layer API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Any


class PlanRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    goal: str = Field(..., min_length=1)


class TaskNodeSchema(BaseModel):
    node_id: str
    title: str
    description: str
    tags: list[str]
    priority: int
    estimated_tokens: int
    dependencies: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskGraphSchema(BaseModel):
    graph_id: str
    goal: str
    nodes: list[TaskNodeSchema]


class CritiqueRequest(BaseModel):
    graph: TaskGraphSchema


class CritiqueReportSchema(BaseModel):
    feasibility: float
    risk: float
    recommendations: list[str]
    notes: str


class MemoryAddRequest(BaseModel):
    key: str
    value: Any
    tags: list[str] = Field(default_factory=list)


class MemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5


class MemorySearchResult(BaseModel):
    key: str
    value: Any
    tags: list[str]
    score: float


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5


class RetrievalResultSchema(BaseModel):
    key: str
    value: Any
    tags: list[str]
    score: float


class IntentRequest(BaseModel):
    goal: str


class IntentSchema(BaseModel):
    intent_type: str
    confidence: float
    entities: list[dict[str, str]]
    raw_goal: str


class UncertaintyRequest(BaseModel):
    node: TaskNodeSchema


class UncertaintyScoreSchema(BaseModel):
    node_id: str
    aleatoric: float
    epistemic: float
    combined: float


class HypothesisRequest(BaseModel):
    observations: list[str]


class HypothesisSchema(BaseModel):
    hypothesis_id: str
    statement: str
    confidence: float
    supporting_observations: list[str]
    contradicting_observations: list[str]


class PolicyRuleRequest(BaseModel):
    rule_id: str
    action_pattern: str
    effect: str
    conditions: dict[str, Any] = Field(default_factory=dict)
    reason: str = ""


class PolicyEvaluateRequest(BaseModel):
    action: str
    context: dict[str, Any] = Field(default_factory=dict)


class PolicyDecisionSchema(BaseModel):
    allowed: bool
    reason: str
    matched_rule: str | None = None


class CausalChainRequest(BaseModel):
    events: list[str]


class CausalLinkSchema(BaseModel):
    cause: str
    effect: str
    confidence: float
    evidence: list[str]


class CausalChainSchema(BaseModel):
    chain_id: str
    events: list[str]
    links: list[CausalLinkSchema]
    summary: str
