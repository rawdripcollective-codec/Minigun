"""HypothesisTester: generates and ranks hypotheses from observations."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class Hypothesis:
    hypothesis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    statement: str = ""
    confidence: float = 0.5
    supporting_observations: list[str] = field(default_factory=list)
    contradicting_observations: list[str] = field(default_factory=list)


_TEMPLATES = [
    ("The observations suggest a configuration issue.", ["config", "setting", "env", "variable"]),
    ("The observations indicate a resource exhaustion problem.", ["memory", "cpu", "disk", "limit", "exceed"]),
    ("The observations point to a network connectivity problem.", ["network", "timeout", "connect", "unreachable"]),
    ("The observations suggest a code logic error.", ["error", "exception", "bug", "fail", "assert"]),
    ("The observations indicate a dependency or version conflict.", ["dependency", "version", "incompatible", "import"]),
    ("The observations suggest a performance bottleneck.", ["slow", "latency", "performance", "throughput"]),
    ("The observations suggest a security policy violation.", ["permission", "denied", "auth", "forbidden", "security"]),
]


def _score_hypothesis(template_keywords: list[str], observations: list[str]) -> float:
    obs_text = " ".join(observations).lower()
    hits = sum(1 for kw in template_keywords if kw in obs_text)
    return round(min(1.0, 0.3 + hits * 0.15), 3)


class HypothesisTester:
    """Generates and ranks hypotheses from observations."""

    def generate(self, observations: list[str]) -> list[Hypothesis]:
        hypotheses: list[Hypothesis] = []

        for statement, keywords in _TEMPLATES:
            confidence = _score_hypothesis(keywords, observations)
            supporting = [o for o in observations if any(kw in o.lower() for kw in keywords)]
            contradicting = [o for o in observations if o not in supporting]
            hypotheses.append(
                Hypothesis(
                    statement=statement,
                    confidence=confidence,
                    supporting_observations=supporting,
                    contradicting_observations=contradicting,
                )
            )

        hypotheses.sort(key=lambda h: h.confidence, reverse=True)
        return hypotheses
