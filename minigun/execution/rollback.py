"""RollbackManager: checkpoint and rollback support."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Checkpoint:
    label: str
    state: dict[str, Any]


class RollbackManager:
    def __init__(self) -> None:
        self._checkpoints: list[Checkpoint] = []

    def checkpoint(self, label: str, state_dict: dict[str, Any]) -> None:
        self._checkpoints.append(Checkpoint(label=label, state=copy.deepcopy(state_dict)))

    def rollback_to(self, label: str) -> dict[str, Any] | None:
        for cp in reversed(self._checkpoints):
            if cp.label == label:
                return copy.deepcopy(cp.state)
        return None

    def list_checkpoints(self) -> list[str]:
        return [cp.label for cp in self._checkpoints]
