"""PRReviewApp: reviews pull request diffs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class PRIssue:
    severity: str  # "error" | "warning" | "info"
    message: str
    line_hint: str = ""


@dataclass
class PRReviewReport:
    issues: list[PRIssue]
    suggestions: list[str]
    risk_level: str  # "low" | "medium" | "high"
    summary: str


_RISK_PATTERNS = [
    (r"DROP TABLE|DELETE FROM|TRUNCATE", "high", "Destructive SQL operation detected."),
    (r"rm -rf|shutil\.rmtree", "high", "Recursive file deletion detected."),
    (r"eval\(|exec\(", "medium", "Dynamic code execution detected."),
    (r"password|secret|token|api_key", "medium", "Potential secret in diff."),
    (r"TODO|FIXME|HACK", "low", "Unresolved TODO/FIXME comment."),
    (r"print\(|console\.log", "low", "Debug print statement found."),
]


class PRReviewApp:
    def review(self, diff: str, context: str = "") -> PRReviewReport:
        issues: list[PRIssue] = []
        highest_risk = "low"

        for pattern, severity, message in _RISK_PATTERNS:
            for m in re.finditer(pattern, diff, re.IGNORECASE):
                line_hint = diff[max(0, m.start() - 40): m.end() + 40].strip()
                issues.append(PRIssue(severity=severity, message=message, line_hint=line_hint))
                if severity == "high":
                    highest_risk = "high"
                elif severity == "medium" and highest_risk == "low":
                    highest_risk = "medium"

        suggestions: list[str] = []
        if "+++ " in diff:
            lines_added = diff.count("\n+")
            if lines_added > 200:
                suggestions.append("PR is large; consider splitting into smaller PRs.")

        if not issues:
            suggestions.append("No critical issues found. LGTM!")

        summary = (
            f"Found {len(issues)} issue(s). Risk level: {highest_risk}."
            if issues
            else "Clean diff – no issues detected."
        )

        return PRReviewReport(
            issues=issues,
            suggestions=suggestions,
            risk_level=highest_risk,
            summary=summary,
        )
