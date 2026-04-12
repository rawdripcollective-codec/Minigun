from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Iterable


DEFAULT_SCOPES_BY_MODE: dict[str, dict[str, set[str]]] = {
    "dev": {
        "anonymous": {
            "connectivity",
            "read_repo",
            "inspect_repo",
        },
    },
    "hardened": {
        "anonymous": {"connectivity"},
    },
}


@dataclass(frozen=True)
class Principal:
    name: str
    scopes: frozenset[str]


@dataclass(frozen=True)
class AuthDecision:
    allowed: bool
    reason: str


class PolicyEngine:
    def __init__(self, mode: str, principals: dict[str, set[str]]) -> None:
        self.mode = mode
        self.principals = principals

    @classmethod
    def from_env(cls) -> "PolicyEngine":
        mode = os.getenv("MINIGUN_POLICY_MODE", "hardened").strip().lower()
        if mode not in DEFAULT_SCOPES_BY_MODE:
            mode = "hardened"

        principals: dict[str, set[str]] = {
            name: set(scopes)
            for name, scopes in DEFAULT_SCOPES_BY_MODE[mode].items()
        }

        policy_json = os.getenv("MINIGUN_POLICY_PRINCIPALS", "").strip()
        if policy_json:
            parsed = json.loads(policy_json)
            if not isinstance(parsed, dict):
                raise ValueError("MINIGUN_POLICY_PRINCIPALS must be a JSON object.")
            for name, scopes in parsed.items():
                if not isinstance(name, str) or not isinstance(scopes, list):
                    raise ValueError(
                        "MINIGUN_POLICY_PRINCIPALS must map principal -> list of scope strings."
                    )
                principals[name] = {str(scope) for scope in scopes}

        return cls(mode=mode, principals=principals)

    def principal(self, name: str) -> Principal:
        scopes = self.principals.get(name, set())
        return Principal(name=name, scopes=frozenset(scopes))

    def authorize(self, principal: Principal, required_scopes: Iterable[str]) -> AuthDecision:
        required = set(required_scopes)
        missing = required - set(principal.scopes)
        if missing:
            return AuthDecision(
                allowed=False,
                reason=f"Missing required scopes: {', '.join(sorted(missing))}",
            )
        return AuthDecision(allowed=True, reason="ok")
