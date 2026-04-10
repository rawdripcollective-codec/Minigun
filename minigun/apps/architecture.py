"""ArchitectureApp: synthesizes architecture diagrams from requirements."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Component:
    name: str
    type: str
    description: str


@dataclass
class Connection:
    from_component: str
    to_component: str
    label: str


@dataclass
class ArchitectureDiagram:
    title: str
    components: list[Component]
    connections: list[Connection]
    rationale: str


_COMPONENT_HINTS: list[tuple[str, str, str]] = [
    ("api|rest|graphql|endpoint", "API Gateway", "api_gateway"),
    ("database|db|postgres|mysql|mongo", "Database", "database"),
    ("cache|redis|memcache", "Cache", "cache"),
    ("queue|kafka|rabbitmq|message", "Message Queue", "message_queue"),
    ("auth|login|oauth|jwt", "Auth Service", "service"),
    ("frontend|ui|react|vue|angular", "Frontend", "frontend"),
    ("worker|job|celery|async task", "Worker", "service"),
    ("storage|s3|blob|file", "Object Storage", "storage"),
    ("monitor|log|metric|trace", "Observability", "service"),
    ("cdn|static|asset", "CDN", "cdn"),
]


class ArchitectureApp:
    def synthesize(self, requirements: str) -> ArchitectureDiagram:
        req_lower = requirements.lower()
        components: list[Component] = []
        seen: set[str] = set()

        for pattern, name, ctype in _COMPONENT_HINTS:
            if re.search(pattern, req_lower):
                if name not in seen:
                    components.append(
                        Component(name=name, type=ctype, description=f"Handles {name.lower()} concerns.")
                    )
                    seen.add(name)

        if not components:
            components = [
                Component(name="Application", type="service", description="Core application service."),
                Component(name="Database", type="database", description="Primary data store."),
            ]

        connections: list[Connection] = []
        for i in range(len(components) - 1):
            connections.append(
                Connection(
                    from_component=components[i].name,
                    to_component=components[i + 1].name,
                    label="calls",
                )
            )

        rationale = (
            f"Architecture composed of {len(components)} components derived from requirements. "
            "Components are connected in a linear flow for simplicity; adapt as needed."
        )

        return ArchitectureDiagram(
            title="Generated Architecture",
            components=components,
            connections=connections,
            rationale=rationale,
        )
