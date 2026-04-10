"""Apps router: /api/v1/apps/*"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Any

from minigun.api.schemas.apps import (
    CodegenRequest, CodegenResultSchema,
    PRReviewRequest, PRReviewReportSchema, PRIssueSchema,
    TestingRequest, TestSuiteSchema, TestCaseSchema,
    ArchitectureRequest, ArchitectureDiagramSchema, ComponentSchema, ConnectionSchema,
    SupportTriageRequest, TriageResultSchema,
    ComplianceRequest, ComplianceReportSchema, ComplianceViolationSchema,
    WorkflowAutomationRequest, AutomationDefSchema, AutomationRunSchema,
)
from minigun.apps.codegen import CodegenApp, CodegenSpec
from minigun.apps.pr_review import PRReviewApp
from minigun.apps.testing import TestingApp
from minigun.apps.architecture import ArchitectureApp
from minigun.apps.support import SupportTriageApp
from minigun.apps.compliance import ComplianceApp
from minigun.apps.workflow_automation import WorkflowAutomationApp

router = APIRouter(prefix="/api/v1/apps", tags=["apps"])

_codegen = CodegenApp()
_pr_review = PRReviewApp()
_testing = TestingApp()
_architecture = ArchitectureApp()
_support = SupportTriageApp()
_compliance = ComplianceApp()
_automation = WorkflowAutomationApp()


@router.post("/codegen", response_model=CodegenResultSchema)
async def codegen(req: CodegenRequest) -> CodegenResultSchema:
    spec = CodegenSpec(
        language=req.language,
        description=req.description,
        class_name=req.class_name,
        functions=req.functions,
    )
    result = _codegen.generate(spec)
    return CodegenResultSchema(language=result.language, code=result.code, warnings=result.warnings)


@router.post("/pr-review", response_model=PRReviewReportSchema)
async def pr_review(req: PRReviewRequest) -> PRReviewReportSchema:
    report = _pr_review.review(req.diff, req.context)
    return PRReviewReportSchema(
        issues=[PRIssueSchema(severity=i.severity, message=i.message, line_hint=i.line_hint) for i in report.issues],
        suggestions=report.suggestions,
        risk_level=report.risk_level,
        summary=report.summary,
    )


@router.post("/testing", response_model=TestSuiteSchema)
async def generate_tests(req: TestingRequest) -> TestSuiteSchema:
    suite = _testing.generate_tests(req.code, req.language)
    return TestSuiteSchema(
        language=suite.language,
        test_cases=[TestCaseSchema(name=t.name, code=t.code, description=t.description) for t in suite.test_cases],
        framework=suite.framework,
    )


@router.post("/architecture", response_model=ArchitectureDiagramSchema)
async def synthesize_architecture(req: ArchitectureRequest) -> ArchitectureDiagramSchema:
    diagram = _architecture.synthesize(req.requirements)
    return ArchitectureDiagramSchema(
        title=diagram.title,
        components=[ComponentSchema(name=c.name, type=c.type, description=c.description) for c in diagram.components],
        connections=[ConnectionSchema(from_component=c.from_component, to_component=c.to_component, label=c.label) for c in diagram.connections],
        rationale=diagram.rationale,
    )


@router.post("/support", response_model=TriageResultSchema)
async def triage_support(req: SupportTriageRequest) -> TriageResultSchema:
    result = _support.triage(req.ticket)
    return TriageResultSchema(
        category=result.category,
        priority=result.priority,
        suggested_actions=result.suggested_actions,
        confidence=result.confidence,
    )


@router.post("/compliance", response_model=ComplianceReportSchema)
async def compliance_check(req: ComplianceRequest) -> ComplianceReportSchema:
    report = _compliance.check(req.artifact, req.standards)
    return ComplianceReportSchema(
        standards_checked=report.standards_checked,
        violations=[
            ComplianceViolationSchema(
                standard=v.standard, rule=v.rule, severity=v.severity, description=v.description
            )
            for v in report.violations
        ],
        warnings=report.warnings,
        passed=report.passed,
        overall_status=report.overall_status,
    )


@router.post("/workflow-automation", response_model=AutomationDefSchema)
async def create_automation(req: WorkflowAutomationRequest) -> AutomationDefSchema:
    auto = _automation.create_automation(req.trigger, req.steps)
    return AutomationDefSchema(
        automation_id=auto.automation_id,
        trigger=auto.trigger,
        steps=auto.steps,
        created_at=auto.created_at,
    )


@router.post("/workflow-automation/{automation_id}/run", response_model=AutomationRunSchema)
async def run_automation(automation_id: str) -> AutomationRunSchema:
    run = _automation.run_automation(automation_id)
    return AutomationRunSchema(
        run_id=run.run_id,
        automation_id=run.automation_id,
        status=run.status.value,
        steps_executed=run.steps_executed,
        outputs=run.outputs,
    )
