"""SupportTriageApp: triages support tickets."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class TriageResult:
    category: str
    priority: str  # "critical" | "high" | "medium" | "low"
    suggested_actions: list[str]
    confidence: float


_CATEGORY_PATTERNS: list[tuple[str, str, list[str], str]] = [
    (
        r"crash|exception|traceback|500|fatal",
        "incident",
        ["Check error logs immediately", "Escalate to on-call engineer", "Create incident report"],
        "critical",
    ),
    (
        r"slow|latency|timeout|performance",
        "performance",
        ["Profile application", "Check resource utilization", "Review recent deployments"],
        "high",
    ),
    (
        r"login|auth|password|access denied|forbidden",
        "auth_issue",
        ["Verify credentials", "Check IAM permissions", "Review auth service logs"],
        "high",
    ),
    (
        r"data|missing|incorrect|wrong|corrupt",
        "data_quality",
        ["Audit recent data changes", "Run data integrity checks", "Review ETL pipelines"],
        "medium",
    ),
    (
        r"feature|request|enhancement|add|improve",
        "feature_request",
        ["Log in backlog", "Prioritise with product team", "Acknowledge requester"],
        "low",
    ),
    (
        r"billing|invoice|payment|charge",
        "billing",
        ["Escalate to billing team", "Verify account status", "Issue refund if applicable"],
        "medium",
    ),
]


class SupportTriageApp:
    def triage(self, ticket: str) -> TriageResult:
        ticket_lower = ticket.lower()
        best_category = "general"
        best_priority = "medium"
        best_actions = ["Acknowledge ticket", "Assign to appropriate team"]
        best_confidence = 0.3

        for pattern, category, actions, priority in _CATEGORY_PATTERNS:
            if re.search(pattern, ticket_lower):
                keyword_count = len(re.findall(pattern, ticket_lower))
                confidence = min(1.0, 0.5 + keyword_count * 0.15)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_category = category
                    best_priority = priority
                    best_actions = actions

        return TriageResult(
            category=best_category,
            priority=best_priority,
            suggested_actions=best_actions,
            confidence=round(best_confidence, 3),
        )
