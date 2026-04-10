"""Tests for the apps layer."""

import pytest
from minigun.apps.codegen import CodegenApp, CodegenSpec
from minigun.apps.pr_review import PRReviewApp
from minigun.apps.testing import TestingApp
from minigun.apps.architecture import ArchitectureApp
from minigun.apps.support import SupportTriageApp
from minigun.apps.compliance import ComplianceApp
from minigun.apps.workflow_automation import WorkflowAutomationApp, RunStatus


# ── CodegenApp ─────────────────────────────────────────────────────────────

def test_codegen_python():
    app = CodegenApp()
    spec = CodegenSpec(language="python", description="parse JSON files", class_name="JsonParser")
    result = app.generate(spec)
    assert result.language == "python"
    assert "JsonParser" in result.code
    assert "class JsonParser" in result.code


def test_codegen_typescript():
    app = CodegenApp()
    spec = CodegenSpec(language="typescript", description="fetch API data", functions=["fetchData"])
    result = app.generate(spec)
    assert "fetchData" in result.code


def test_codegen_go():
    app = CodegenApp()
    spec = CodegenSpec(language="go", description="process messages")
    result = app.generate(spec)
    assert "package generated" in result.code


def test_codegen_unknown_language():
    app = CodegenApp()
    spec = CodegenSpec(language="brainfuck", description="hello world")
    result = app.generate(spec)
    assert len(result.warnings) > 0


# ── PRReviewApp ────────────────────────────────────────────────────────────

def test_pr_review_clean_diff():
    app = PRReviewApp()
    report = app.review("--- a/main.py\n+++ b/main.py\n@@ -1 +1 @@\n-old = 1\n+new = 2")
    assert report.risk_level == "low"
    assert len(report.suggestions) > 0


def test_pr_review_dangerous_diff():
    app = PRReviewApp()
    diff = "--- a/db.py\n+++ b/db.py\n+exec(user_input)\n+password = 'hardcoded'"
    report = app.review(diff)
    assert report.risk_level in {"medium", "high"}
    assert len(report.issues) > 0


def test_pr_review_sql_danger():
    app = PRReviewApp()
    report = app.review("+ DROP TABLE users")
    assert report.risk_level == "high"


# ── TestingApp ─────────────────────────────────────────────────────────────

def test_testing_python():
    app = TestingApp()
    code = "def add(a, b):\n    return a + b\n\ndef multiply(x, y):\n    return x * y"
    suite = app.generate_tests(code, "python")
    assert suite.framework == "pytest"
    assert any(tc.name == "test_add" for tc in suite.test_cases)


def test_testing_no_functions():
    app = TestingApp()
    suite = app.generate_tests("# empty module", "python")
    assert len(suite.test_cases) > 0  # falls back to "main"


def test_testing_other_language():
    app = TestingApp()
    suite = app.generate_tests("class Foo {}", "java")
    assert suite.language == "java"
    assert len(suite.test_cases) > 0


# ── ArchitectureApp ────────────────────────────────────────────────────────

def test_architecture_with_keywords():
    app = ArchitectureApp()
    diagram = app.synthesize("Build a REST API with database and cache and auth")
    names = {c.name for c in diagram.components}
    assert "API Gateway" in names or "Database" in names


def test_architecture_default_fallback():
    app = ArchitectureApp()
    diagram = app.synthesize("do something vague")
    assert len(diagram.components) >= 2
    assert len(diagram.rationale) > 0


def test_architecture_connections():
    app = ArchitectureApp()
    diagram = app.synthesize("api with database and frontend")
    assert len(diagram.connections) > 0


# ── SupportTriageApp ───────────────────────────────────────────────────────

def test_support_crash():
    app = SupportTriageApp()
    result = app.triage("App crashes with a fatal exception at startup")
    assert result.category == "incident"
    assert result.priority == "critical"


def test_support_feature_request():
    app = SupportTriageApp()
    result = app.triage("I would like to request a new feature to improve reporting")
    assert result.category == "feature_request"
    assert result.priority == "low"


def test_support_auth_issue():
    app = SupportTriageApp()
    result = app.triage("Login fails with access denied error")
    assert result.category == "auth_issue"
    assert len(result.suggested_actions) > 0


def test_support_low_confidence_fallback():
    app = SupportTriageApp()
    result = app.triage("Hello I have a question")
    assert result.confidence >= 0.3


# ── ComplianceApp ──────────────────────────────────────────────────────────

def test_compliance_clean():
    app = ComplianceApp()
    report = app.check("def hello(): return 'world'", ["OWASP"])
    assert report.overall_status in {"pass", "warning"}


def test_compliance_violation():
    app = ComplianceApp()
    report = app.check("query = 'SELECT * FROM users WHERE id = ' + user_id", ["OWASP"])
    assert report.overall_status == "fail"
    assert len(report.violations) > 0


def test_compliance_multiple_standards():
    app = ComplianceApp()
    report = app.check("logging.info(user_email)", ["GDPR", "SOC2"])
    assert "GDPR" in report.standards_checked
    assert "SOC2" in report.standards_checked


# ── WorkflowAutomationApp ──────────────────────────────────────────────────

def test_automation_create_and_run():
    app = WorkflowAutomationApp()
    trigger = {"event": "push", "branch": "main"}
    steps = [{"name": "build"}, {"name": "test"}, {"name": "deploy"}]
    auto = app.create_automation(trigger, steps)
    assert auto.automation_id is not None

    run = app.run_automation(auto.automation_id)
    assert run.status == RunStatus.COMPLETED
    assert run.steps_executed == 3


def test_automation_run_missing_id():
    app = WorkflowAutomationApp()
    run = app.run_automation("nonexistent-id")
    assert run.status == RunStatus.FAILED
    assert run.steps_executed == 0
