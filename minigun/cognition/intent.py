"""IntentInferencer: classifies free-text goal into an Intent."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_INTENT_PATTERNS: list[tuple[str, list[str]]] = [
    ("codegen", ["generat", "creat", "write", "build", "implement", "code"]),
    ("testing", ["test", "spec", "verify", "qa", "assert"]),
    ("deployment", ["deploy", "release", "ship", "launch", "publish"]),
    ("review", ["review", "audit", "inspect", "check", "analys"]),
    ("research", ["research", "investig", "explore", "understand", "explain"]),
    ("monitoring", ["monitor", "observ", "alert", "watch", "track"]),
    ("security", ["secur", "vulnerab", "pentest", "hardening", "compliance"]),
    ("documentation", ["document", "readme", "wiki", "guide", "manual"]),
    ("refactor", ["refactor", "clean", "restructur", "reorganiz", "simplif"]),
    ("data", ["data", "database", "migrat", "schema", "query"]),
]

_ENTITY_PATTERNS: list[tuple[str, str]] = [
    (r"\b([A-Z][a-zA-Z0-9_]+(?:App|Service|API|Manager|Engine|Controller))\b", "component"),
    (r"\bhttps?://\S+", "url"),
    (r"\b(?:Python|Go|Rust|Java|TypeScript|JavaScript|C\+\+)\b", "language"),
    (r"\b(?:AWS|GCP|Azure|Kubernetes|Docker|Terraform)\b", "platform"),
]


@dataclass
class Intent:
    intent_type: str
    confidence: float
    entities: list[dict[str, str]] = field(default_factory=list)
    raw_goal: str = ""


class IntentInferencer:
    """Classifies free-text goal into an Intent."""

    def infer(self, goal: str) -> Intent:
        goal_lower = goal.lower()
        scores: dict[str, float] = {}

        for intent_type, keywords in _INTENT_PATTERNS:
            count = sum(1 for kw in keywords if kw in goal_lower)
            if count:
                scores[intent_type] = count / len(keywords)

        if scores:
            best = max(scores, key=lambda k: scores[k])
            confidence = round(min(1.0, scores[best] * 2), 3)
        else:
            best = "general"
            confidence = 0.3

        entities: list[dict[str, str]] = []
        for pattern, etype in _ENTITY_PATTERNS:
            for match in re.finditer(pattern, goal):
                entities.append({"type": etype, "value": match.group()})

        return Intent(
            intent_type=best,
            confidence=confidence,
            entities=entities,
            raw_goal=goal,
        )
