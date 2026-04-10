"""PolicyEngine: enforces allow/deny rules for actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PolicyRule:
    rule_id: str
    action_pattern: str   # glob-style, e.g. "deploy:*"
    effect: str           # "allow" or "deny"
    conditions: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str
    matched_rule: str | None = None


def _matches(pattern: str, action: str) -> bool:
    """Simple wildcard match: * matches any sequence of chars."""
    import fnmatch
    return fnmatch.fnmatch(action.lower(), pattern.lower())


class PolicyEngine:
    """Evaluates actions against a set of allow/deny rules."""

    def __init__(self) -> None:
        self._rules: list[PolicyRule] = []
        # Default: allow everything
        self._default_effect = "allow"

    def add_rule(self, rule: PolicyRule) -> None:
        self._rules.append(rule)

    def remove_rule(self, rule_id: str) -> None:
        self._rules = [r for r in self._rules if r.rule_id != rule_id]

    def list_rules(self) -> list[PolicyRule]:
        return list(self._rules)

    def evaluate(self, action: str, context: dict[str, Any] | None = None) -> PolicyDecision:
        """Return PolicyDecision for the given action and context."""
        ctx = context or {}

        # Deny rules take precedence; check deny first
        for rule in self._rules:
            if rule.effect == "deny" and _matches(rule.action_pattern, action):
                if self._conditions_match(rule.conditions, ctx):
                    return PolicyDecision(
                        allowed=False,
                        reason=rule.reason or f"Denied by rule {rule.rule_id}",
                        matched_rule=rule.rule_id,
                    )

        for rule in self._rules:
            if rule.effect == "allow" and _matches(rule.action_pattern, action):
                if self._conditions_match(rule.conditions, ctx):
                    return PolicyDecision(
                        allowed=True,
                        reason=rule.reason or f"Allowed by rule {rule.rule_id}",
                        matched_rule=rule.rule_id,
                    )

        # Fall back to default
        allowed = self._default_effect == "allow"
        return PolicyDecision(
            allowed=allowed,
            reason=f"No matching rule; default effect is '{self._default_effect}'",
            matched_rule=None,
        )

    @staticmethod
    def _conditions_match(conditions: dict[str, Any], ctx: dict[str, Any]) -> bool:
        for k, v in conditions.items():
            if ctx.get(k) != v:
                return False
        return True
