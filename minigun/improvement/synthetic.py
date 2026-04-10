"""SyntheticTaskGenerator: generates synthetic tasks for a domain."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class SyntheticTask:
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain: str = ""
    description: str = ""
    expected_output_hint: str = ""
    difficulty: str = "medium"
    tags: list[str] = field(default_factory=list)


_DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

_DOMAIN_TEMPLATES: dict[str, list[str]] = {
    "codegen": [
        "Write a {lang} function that {action}",
        "Implement a {lang} class for {concept}",
        "Create a REST endpoint in {lang} that {action}",
    ],
    "testing": [
        "Write unit tests for a {lang} function that {action}",
        "Create integration tests for the {concept} service",
    ],
    "devops": [
        "Write a Dockerfile for a {lang} application",
        "Create a CI pipeline for {concept}",
        "Implement blue-green deployment for {concept}",
    ],
    "security": [
        "Audit this {lang} code for SQL injection vulnerabilities",
        "Implement OAuth2 authentication for {concept}",
    ],
}

_LANG_OPTIONS = ["Python", "Go", "TypeScript", "Rust"]
_ACTION_OPTIONS = ["sorts a list", "validates email", "parses JSON", "computes Fibonacci"]
_CONCEPT_OPTIONS = ["user management", "payment processing", "notification service", "data pipeline"]


class SyntheticTaskGenerator:
    def generate(self, domain: str, n: int) -> list[SyntheticTask]:
        templates = _DOMAIN_TEMPLATES.get(domain.lower(), _DOMAIN_TEMPLATES["codegen"])
        tasks: list[SyntheticTask] = []

        for i in range(n):
            tmpl = templates[i % len(templates)]
            lang = _LANG_OPTIONS[i % len(_LANG_OPTIONS)]
            action = _ACTION_OPTIONS[i % len(_ACTION_OPTIONS)]
            concept = _CONCEPT_OPTIONS[i % len(_CONCEPT_OPTIONS)]
            description = tmpl.format(lang=lang, action=action, concept=concept)
            difficulty = _DIFFICULTY_LEVELS[i % len(_DIFFICULTY_LEVELS)]

            tasks.append(
                SyntheticTask(
                    domain=domain,
                    description=description,
                    expected_output_hint=f"Expected: working {lang} implementation",
                    difficulty=difficulty,
                    tags=[domain, lang.lower(), difficulty],
                )
            )
        return tasks
