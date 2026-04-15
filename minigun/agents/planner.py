"""Planner Agent – decomposes high-level intents into TaskGraphs."""

from __future__ import annotations

import logging
from typing import Any

from minigun.models.core import IntentRequest, Task, TaskGraph, TaskStatus

logger = logging.getLogger(__name__)

# Maps keywords in the intent to domain solver names
_DOMAIN_MAP: dict[str, str] = {
    "feature": "code",
    "bug": "code",
    "code": "code",
    "refactor": "code",
    "test": "code",
    "deploy": "infra",
    "infra": "infra",
    "kubernetes": "infra",
    "terraform": "infra",
    "docker": "infra",
    "scale": "infra",
    "incident": "sre",
    "alert": "sre",
    "remediat": "sre",
    "rollback": "sre",
    "postmortem": "sre",
    "monitor": "sre",
    "data": "data",
    "analytics": "data",
    "pipeline": "data",
    "etl": "data",
    "report": "data",
}

# Per-domain task templates: list of (name, type, solver)
_TASK_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "code": [
        {"name": "Analyse codebase", "type": "code", "solver": "code"},
        {"name": "Implement changes", "type": "code", "solver": "code"},
        {"name": "Run tests", "type": "code", "solver": "code"},
        {"name": "Security scan", "type": "code", "solver": "code"},
        {"name": "Open pull request", "type": "code", "solver": "code"},
    ],
    "infra": [
        {"name": "Terraform plan", "type": "infra", "solver": "infra"},
        {"name": "Terraform apply", "type": "infra", "solver": "infra"},
        {"name": "Deploy to Kubernetes", "type": "infra", "solver": "infra"},
        {"name": "Verify deployment health", "type": "infra", "solver": "infra"},
    ],
    "sre": [
        {"name": "Triage incident", "type": "sre", "solver": "sre"},
        {"name": "Identify root cause", "type": "sre", "solver": "sre"},
        {"name": "Apply remediation", "type": "sre", "solver": "sre"},
        {"name": "Verify system recovery", "type": "sre", "solver": "sre"},
        {"name": "Generate postmortem", "type": "sre", "solver": "sre"},
    ],
    "data": [
        {"name": "Validate data sources", "type": "data", "solver": "data"},
        {"name": "Run ETL pipeline", "type": "data", "solver": "data"},
        {"name": "Verify data quality", "type": "data", "solver": "data"},
        {"name": "Publish report", "type": "data", "solver": "data"},
    ],
}


class PlannerAgent:
    """Analyses an intent and decomposes it into a concrete TaskGraph."""

    def _detect_domain(self, intent: str) -> str:
        intent_lower = intent.lower()
        for keyword, domain in _DOMAIN_MAP.items():
            if keyword in intent_lower:
                return domain
        return "code"  # sensible default

    def plan(self, intent_request: IntentRequest) -> TaskGraph:
        """Decompose an IntentRequest into a TaskGraph with ordered tasks."""
        logger.info("Planning intent: %s", intent_request.intent)

        domain = self._detect_domain(intent_request.intent)
        templates = _TASK_TEMPLATES.get(domain, _TASK_TEMPLATES["code"])

        tasks: list[Task] = []
        for tmpl in templates:
            task = Task(
                name=tmpl["name"],
                type=tmpl["type"],
                assigned_solver=tmpl["solver"],
                inputs={"intent": intent_request.intent, "context": intent_request.context},
                status=TaskStatus.PENDING,
            )
            tasks.append(task)

        # Build a linear dependency chain: each task depends on the previous
        edges: list[tuple[str, str]] = []
        for i in range(1, len(tasks)):
            edges.append((tasks[i - 1].id, tasks[i].id))
            tasks[i].dependencies = [tasks[i - 1].id]

        graph = TaskGraph(
            intent=intent_request.intent,
            tasks=tasks,
            edges=edges,
            status=TaskStatus.PENDING,
        )

        logger.info(
            "Planned graph id=%s domain=%s tasks=%d",
            graph.id,
            domain,
            len(tasks),
        )
        return graph
