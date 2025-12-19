"""Unit tests for TimerRequest mock."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Project/Local
from azure_functions_test import mock_timer_request


# =============================================================================
# TESTS: Initialization & Defaults
# =============================================================================
def test_mock_timer_request_uses_defaults_when_no_args() -> None:
    """mock_timer_request() should use default values when called with no args."""
    timer = mock_timer_request()

    assert timer.past_due is False


def test_mock_timer_request_default_not_past_due() -> None:
    """Timer should not be past due by default."""
    timer = mock_timer_request()

    assert timer.past_due is False


# =============================================================================
# TESTS: Past Due Flag
# =============================================================================
def test_mock_timer_request_past_due_true() -> None:
    """Timer with past_due=True should be marked as past due."""
    timer = mock_timer_request(past_due=True)

    assert timer.past_due is True


def test_mock_timer_request_past_due_false() -> None:
    """Timer with past_due=False should not be past due."""
    timer = mock_timer_request(past_due=False)

    assert timer.past_due is False


# =============================================================================
# TESTS: Multiple Instances
# =============================================================================
def test_mock_timer_request_multiple_instances_independent() -> None:
    """Multiple timer instances should be independent."""
    timer1 = mock_timer_request(past_due=True)
    timer2 = mock_timer_request(past_due=False)

    assert timer1.past_due is True
    assert timer2.past_due is False


# =============================================================================
# TESTS: Integration with Real Use Cases
# =============================================================================
def test_mock_timer_request_on_time_execution() -> None:
    """Should support testing on-time timer execution."""
    timer = mock_timer_request(past_due=False)

    # Simulate on-time execution check
    execution_status = "on-time" if not timer.past_due else "delayed"

    assert execution_status == "on-time"


def test_mock_timer_request_delayed_execution() -> None:
    """Should support testing delayed timer execution."""
    timer = mock_timer_request(past_due=True)

    # Simulate delayed execution check
    execution_status = "delayed" if timer.past_due else "on-time"

    assert execution_status == "delayed"


def test_mock_timer_request_conditional_logic() -> None:
    """Should support testing conditional logic based on past_due."""
    timer_delayed = mock_timer_request(past_due=True)
    timer_on_time = mock_timer_request(past_due=False)

    # Test delayed timer triggers retry logic
    assert timer_delayed.past_due is True

    # Test on-time timer proceeds normally
    assert timer_on_time.past_due is False
