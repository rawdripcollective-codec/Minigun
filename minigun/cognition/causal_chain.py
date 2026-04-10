"""CausalChainEngine: builds causal explanation chains for event sequences."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CausalLink:
    cause: str
    effect: str
    confidence: float
    evidence: list[str] = field(default_factory=list)


@dataclass
class CausalChain:
    chain_id: str
    events: list[str]
    links: list[CausalLink]
    summary: str


import uuid


def _simple_cause_effect(events: list[str]) -> list[CausalLink]:
    """Generate sequential cause→effect links between consecutive events."""
    links = []
    for i in range(len(events) - 1):
        confidence = max(0.3, 1.0 - i * 0.08)
        links.append(
            CausalLink(
                cause=events[i],
                effect=events[i + 1],
                confidence=round(confidence, 2),
                evidence=[f"Temporal proximity between event {i} and event {i+1}"],
            )
        )
    return links


class CausalChainEngine:
    """Builds a causal explanation chain for a sequence of events."""

    def build_chain(self, events: list[str]) -> CausalChain:
        links = _simple_cause_effect(events)
        summary = (
            f"Chain of {len(events)} events with {len(links)} causal links identified."
            if events
            else "No events provided."
        )
        return CausalChain(
            chain_id=str(uuid.uuid4()),
            events=events,
            links=links,
            summary=summary,
        )
