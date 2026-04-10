"""RewardModel: scores trajectories for reinforcement learning."""

from __future__ import annotations

from typing import Any


class RewardModel:
    """Heuristic reward model for agent trajectories."""

    def score(self, trajectory: list[dict[str, Any]]) -> float:
        if not trajectory:
            return 0.0

        total = 0.0
        for step in trajectory:
            # Reward for successful steps
            if step.get("success", False):
                total += 1.0
            # Bonus for efficient steps (few retries)
            retries = step.get("retries", 0)
            total += max(0.0, 0.5 - retries * 0.1)
            # Penalty for errors
            if step.get("error"):
                total -= 0.5

        # Normalise
        max_possible = len(trajectory) * 1.5
        score = max(0.0, min(1.0, total / max_possible))
        return round(score, 4)
