"""ComplianceApp: checks artifacts against compliance standards."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ComplianceViolation:
    standard: str
    rule: str
    severity: str
    description: str


@dataclass
class ComplianceReport:
    standards_checked: list[str]
    violations: list[ComplianceViolation]
    warnings: list[str]
    passed: list[str]
    overall_status: str  # "pass" | "fail" | "warning"


_RULES: dict[str, list[tuple[str, str, str]]] = {
    "PCI-DSS": [
        (r"password\s*=\s*['\"][^'\"]+['\"]", "Hard-coded password detected.", "violation"),
        (r"credit.?card|pan\b|cvv", "PCI data in artifact.", "violation"),
    ],
    "GDPR": [
        (r"email|phone|address|ssn|social.security", "Potential PII in artifact.", "warning"),
        (r"consent|gdpr|data.protection", "", "pass"),
    ],
    "SOC2": [
        (r"logging|audit|monitor", "", "pass"),
        (r"encrypt|tls|ssl|https", "", "pass"),
        (r"http://(?!localhost)", "Non-TLS HTTP usage detected.", "warning"),
    ],
    "OWASP": [
        (r"eval\(|exec\(", "Potential code injection vector.", "violation"),
        (r"SELECT \*", "Broad SELECT may expose sensitive data.", "warning"),
        (r"(?:sql|query).*=.*\+|(?:sql|query).*format\(", "Potential SQL injection.", "violation"),
    ],
}


class ComplianceApp:
    def check(self, artifact: str, standards: list[str]) -> ComplianceReport:
        violations: list[ComplianceViolation] = []
        warnings: list[str] = []
        passed: list[str] = []

        for standard in standards:
            rules = _RULES.get(standard.upper(), [])
            standard_passed = True
            for pattern, description, severity in rules:
                if not pattern:
                    continue
                if re.search(pattern, artifact, re.IGNORECASE):
                    if severity == "violation":
                        violations.append(
                            ComplianceViolation(
                                standard=standard,
                                rule=pattern,
                                severity="high",
                                description=description,
                            )
                        )
                        standard_passed = False
                    elif severity == "warning":
                        warnings.append(f"[{standard}] {description}")
                    elif severity == "pass":
                        passed.append(f"[{standard}] Pattern found: {description or pattern}")

            if standard_passed and not any(v.standard == standard for v in violations):
                passed.append(f"{standard}: basic checks passed.")

        if violations:
            overall = "fail"
        elif warnings:
            overall = "warning"
        else:
            overall = "pass"

        return ComplianceReport(
            standards_checked=standards,
            violations=violations,
            warnings=warnings,
            passed=passed,
            overall_status=overall,
        )
