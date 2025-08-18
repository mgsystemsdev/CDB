# src/core/services/points.py
# Author: Miguel Gonzalez Almonte
# Created: 2025-08-17
# Description: Implements pure functions for calculating points from sessions.
# Role: Core logic

from __future__ import annotations

from typing import Dict

from core.types.enums import Difficulty, SessionStatus

DEFAULT_WEIGHTS: Dict[Difficulty, float] = {
    Difficulty.beginner: 1.0,
    Difficulty.intermediate: 1.3,
    Difficulty.advanced: 1.6,
    Difficulty.expert: 2.0,
}


def compute_points(
    hours_spent: float,
    difficulty: Difficulty,
    status: SessionStatus,
    weights: Dict[Difficulty, float] = DEFAULT_WEIGHTS,
) -> float:
    """
    Compute gamification points from a session.

    - Cancelled sessions always = 0
    - Otherwise: hours_spent × weight[difficulty]
    - Rounded to 2 decimals
    """
    if status == SessionStatus.cancelled:
        return 0.0

    multiplier = weights.get(difficulty, 1.0)
    points = hours_spent * multiplier
    return round(points, 2)
