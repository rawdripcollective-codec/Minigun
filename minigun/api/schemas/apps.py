"""Pydantic schemas for the Apps layer API."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class CodegenRequest(BaseModel):
    language: str
    description: str
    class_name: str = "GeneratedClass"
    functions: list[str] | None = None


class CodegenResultSchema(BaseModel):
    language: str
    code: str
    warnings: list[str]


class PRReviewRequest(BaseModel):
    diff: str
    context: str = ""


class PRIssueSchema(BaseModel):
    severity: str
    message: str
    line_hint: str


class PRReviewReportSchema(BaseModel):
    issues: list[PRIssueSchema]
    suggestions: list[str]
    risk_level: str
    summary: str


class TestingRequest(BaseModel):
    code: str
    language: str


class TestCaseSchema(BaseModel):
    name: str
    code: str
    description: str


class TestSuiteSchema(BaseModel):
    language: str
    test_cases: list[TestCaseSchema]
    framework: str


class ArchitectureRequest(BaseModel):
    requirements: str


class ComponentSchema(BaseModel):
    name: str
    type: str
    description: str


class ConnectionSchema(BaseModel):
    from_component: str
    to_component: str
    label: str


class ArchitectureDiagramSchema(BaseModel):
    title: str
    components: list[ComponentSchema]
    connections: list[ConnectionSchema]
    rationale: str


class SupportTriageRequest(BaseModel):
    ticket: str


class TriageResultSchema(BaseModel):
    category: str
    priority: str
    suggested_actions: list[str]
    confidence: float


class ComplianceRequest(BaseModel):
    artifact: str
    standards: list[str]


class ComplianceViolationSchema(BaseModel):
    standard: str
    rule: str
    severity: str
    description: str


class ComplianceReportSchema(BaseModel):
    standards_checked: list[str]
    violations: list[ComplianceViolationSchema]
    warnings: list[str]
    passed: list[str]
    overall_status: str


class WorkflowAutomationRequest(BaseModel):
    trigger: dict[str, Any]
    steps: list[dict[str, Any]]


class AutomationDefSchema(BaseModel):
    automation_id: str
    trigger: dict[str, Any]
    steps: list[dict[str, Any]]
    created_at: str


class AutomationRunSchema(BaseModel):
    run_id: str
    automation_id: str
    status: str
    steps_executed: int
    outputs: list[Any]
