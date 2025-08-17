# tests/unit/test_points.py
# Author: Miguel Gonzalez Almonte
# Created: 2025-08-17
# Description: Unit test for core points calculation logic. Checks formulas involving hours × difficulty × status remain correct.
# Role: Infrastructure/UI/Tests/Config

import pytest
from core.services.points import compute_points, DEFAULT_WEIGHTS
from core.types.enums import Difficulty, SessionStatus


@pytest.mark.parametrize(
    "hours,difficulty,status,expected",
    [
        # Test basic points calculation
        (1.0, Difficulty.beginner, SessionStatus.completed, 1.0),
        (1.0, Difficulty.intermediate, SessionStatus.completed, 1.3),
        (1.0, Difficulty.advanced, SessionStatus.completed, 1.6),
        (1.0, Difficulty.expert, SessionStatus.completed, 2.0),
        
        # Test hours multiplication
        (2.0, Difficulty.beginner, SessionStatus.completed, 2.0),
        (2.5, Difficulty.intermediate, SessionStatus.completed, 3.25),
        
        # Test cancelled sessions
        (1.0, Difficulty.beginner, SessionStatus.cancelled, 0.0),
        (2.0, Difficulty.expert, SessionStatus.cancelled, 0.0),
        
        # Test rounding to 2 decimals
        (1.5, Difficulty.intermediate, SessionStatus.completed, 1.95),  # 1.5 * 1.3
        (2.7, Difficulty.advanced, SessionStatus.completed, 4.32),      # 2.7 * 1.6
    ]
)
def test_compute_points(hours, difficulty, status, expected):
    """Test points computation with different combinations of inputs."""
    points = compute_points(hours, difficulty, status)
    assert points == expected


def test_custom_weights():
    """Test compute_points with custom difficulty weights."""
    custom_weights = {
        Difficulty.beginner: 1.5,
        Difficulty.intermediate: 2.0,
        Difficulty.advanced: 2.5,
        Difficulty.expert: 3.0,
    }
    
    points = compute_points(
        hours_spent=1.0,
        difficulty=Difficulty.intermediate,
        status=SessionStatus.completed,
        weights=custom_weights
    )
    assert points == 2.0  # 1.0 * 2.0


def test_fallback_weight():
    """Test compute_points with missing difficulty in weights."""
    weights = {}  # Empty weights dictionary
    points = compute_points(
        hours_spent=1.0,
        difficulty=Difficulty.beginner,
        status=SessionStatus.completed,
        weights=weights
    )
    assert points == 1.0  # Should use fallback multiplier of 1.0


def test_default_weights_immutable():
    """Test that DEFAULT_WEIGHTS cannot be modified."""
    original_weights = DEFAULT_WEIGHTS.copy()
    
    # Try to modify through compute_points
    custom_weights = DEFAULT_WEIGHTS.copy()
    custom_weights[Difficulty.beginner] = 99.9
    compute_points(1.0, Difficulty.beginner, SessionStatus.completed, custom_weights)
    
    # Verify DEFAULT_WEIGHTS remained unchanged
    assert DEFAULT_WEIGHTS == original_weights
