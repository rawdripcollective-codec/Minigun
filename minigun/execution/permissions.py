"""PermissionManager: grant/revoke/check permissions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionKey:
    principal: str
    resource: str
    action: str


class PermissionManager:
    def __init__(self) -> None:
        self._grants: set[PermissionKey] = set()

    def grant(self, principal: str, resource: str, action: str) -> None:
        self._grants.add(PermissionKey(principal, resource, action))

    def revoke(self, principal: str, resource: str, action: str) -> None:
        self._grants.discard(PermissionKey(principal, resource, action))

    def check(self, principal: str, resource: str, action: str) -> bool:
        # Exact match or wildcard action
        return (
            PermissionKey(principal, resource, action) in self._grants
            or PermissionKey(principal, resource, "*") in self._grants
            or PermissionKey(principal, "*", action) in self._grants
            or PermissionKey(principal, "*", "*") in self._grants
        )

    def list_grants(self) -> list[dict[str, str]]:
        return [
            {"principal": k.principal, "resource": k.resource, "action": k.action}
            for k in self._grants
        ]
