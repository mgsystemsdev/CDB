# tests/unit/test_progress.py
# Author: Miguel Gonzalez Almonte
# Created: 2025-08-17
# Description: Unit test for progress accumulation logic. Ensures clamping and rounding of percentages behaves correctly.
# Role: Infrastructure/UI/Tests/Config

from dataclasses import dataclass
import pytest
from core.services.progress import (
    accumulate_hours,
    compute_progress,
    progress_from_sessions,
    ProgressReport,
)


@dataclass
class MockSession:
    """Mock session class for testing."""
    hours: float


def test_accumulate_hours_empty():
    """Test accumulating hours with empty session list."""
    assert accumulate_hours([]) == 0.0


def test_accumulate_hours():
    """Test accumulating hours from multiple sessions."""
    sessions = [
        MockSession(hours=1.5),
        MockSession(hours=2.0),
        MockSession(hours=0.5),
    ]
    assert accumulate_hours(sessions) == 4.0


def test_accumulate_hours_with_zero():
    """Test accumulating hours including zero-hour sessions."""
    sessions = [
        MockSession(hours=1.5),
        MockSession(hours=0.0),
        MockSession(hours=2.5),
    ]
    assert accumulate_hours(sessions) == 4.0


@pytest.mark.parametrize(
    "total_hours,target_hours,expected",
    [
        # Basic progress calculations
        (5.0, 10.0, ProgressReport(5.0, 10.0, 50.0)),
        (10.0, 10.0, ProgressReport(10.0, 10.0, 100.0)),
        (0.0, 10.0, ProgressReport(0.0, 10.0, 0.0)),
        
        # Edge cases
        (15.0, 10.0, ProgressReport(15.0, 10.0, 100.0)),  # Over 100%
        (0.0, 0.0, ProgressReport(0.0, 0.0, 0.0)),        # Zero target
        
        # Negative values handling
            (-5.0, 10.0, ProgressReport(0.0, 10.0, 0.0)),     # Negative hours
            (5.0, -10.0, ProgressReport(5.0, 0.0, 0.0)),      # Negative target
            
            # Rounding tests
            (3.336, 10.0, ProgressReport(3.34, 10.0, 33.36)),
            (10.666, 20.0, ProgressReport(10.67, 20.0, 53.33)),
    ]
)
def test_compute_progress(total_hours, target_hours, expected):
    """Test progress computation with various scenarios."""
    result = compute_progress(total_hours, target_hours)
    assert result == expected


def test_compute_progress_zero_values():
    """Test progress computation with zero values."""
    assert compute_progress(0.0, 10.0) == ProgressReport(0.0, 10.0, 0.0)
    assert compute_progress(5.0, 0.0) == ProgressReport(5.0, 0.0, 0.0)
    assert compute_progress(0.0, 0.0) == ProgressReport(0.0, 0.0, 0.0)


def test_progress_from_sessions():
    """Test high-level progress computation from sessions."""
    sessions = [
        MockSession(hours=1.5),
        MockSession(hours=2.0),
        MockSession(hours=1.5)
    ]
    result = progress_from_sessions(sessions, target_hours=10.0)
    assert result == ProgressReport(5.0, 10.0, 50.0)


def test_progress_from_sessions_empty():
    """Test progress computation with empty session list."""
    result = progress_from_sessions([], target_hours=10.0)
    assert result == ProgressReport(0.0, 10.0, 0.0)


def test_progress_report_immutability():
    """Test that ProgressReport is immutable (frozen)."""
    report = ProgressReport(total_hours=5.0, target_hours=10.0, percent_complete=50.0)
    with pytest.raises(AttributeError):
        report.total_hours = 6.0  # Should raise error due to frozen=True
