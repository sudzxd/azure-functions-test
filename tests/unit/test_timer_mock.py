"""Unit tests for TimerRequest mock."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from datetime import UTC, datetime, timedelta

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
# TESTS: Schedule Status
# =============================================================================
def test_mock_timer_request_default_schedule_status() -> None:
    """Timer should have default schedule_status with Last/Next/LastUpdated."""
    timer = mock_timer_request()

    assert "Last" in timer.schedule_status
    assert "Next" in timer.schedule_status
    assert "LastUpdated" in timer.schedule_status
    assert isinstance(timer.schedule_status["Last"], datetime)
    assert isinstance(timer.schedule_status["Next"], datetime)
    assert isinstance(timer.schedule_status["LastUpdated"], datetime)


def test_mock_timer_request_custom_schedule_status() -> None:
    """Timer should accept custom schedule_status."""
    last_run = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    next_run = datetime(2025, 1, 1, 13, 0, tzinfo=UTC)

    timer = mock_timer_request(
        schedule_status={
            "Last": last_run,
            "Next": next_run,
            "LastUpdated": datetime.now(UTC),
        }
    )

    assert timer.schedule_status["Last"] == last_run
    assert timer.schedule_status["Next"] == next_run


def test_mock_timer_request_schedule_status_ordering() -> None:
    """Schedule status Last should be before Next."""
    now = datetime.now(UTC)
    timer = mock_timer_request(
        schedule_status={
            "Last": now - timedelta(hours=1),
            "Next": now + timedelta(hours=1),
            "LastUpdated": now,
        }
    )

    assert timer.schedule_status["Last"] < timer.schedule_status["Next"]


def test_mock_timer_request_schedule_status_with_timezone() -> None:
    """Schedule status times should include timezone information."""
    timer = mock_timer_request()

    assert timer.schedule_status["Last"].tzinfo is not None
    assert timer.schedule_status["Next"].tzinfo is not None
    assert timer.schedule_status["LastUpdated"].tzinfo is not None


# =============================================================================
# TESTS: Schedule Configuration
# =============================================================================
def test_mock_timer_request_default_schedule_empty() -> None:
    """Timer should have empty schedule dict by default."""
    timer = mock_timer_request()

    assert timer.schedule == {}


def test_mock_timer_request_custom_schedule() -> None:
    """Timer should accept custom schedule configuration."""
    schedule_config = {
        "AdjustForDST": True,
        "Expression": "0 */5 * * * *",  # Every 5 minutes
        "RunOnStartup": False,
    }

    timer = mock_timer_request(schedule=schedule_config)

    assert timer.schedule["AdjustForDST"] is True
    assert timer.schedule["Expression"] == "0 */5 * * * *"
    assert timer.schedule["RunOnStartup"] is False


def test_mock_timer_request_schedule_with_cron_expression() -> None:
    """Timer schedule should support cron expressions."""
    timer = mock_timer_request(
        schedule={"Expression": "0 0 */6 * * *"}  # Every 6 hours
    )

    assert timer.schedule["Expression"] == "0 0 */6 * * *"


# =============================================================================
# TESTS: Combined Properties
# =============================================================================
def test_mock_timer_request_all_properties() -> None:
    """Timer should support all properties together."""
    last_run = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    next_run = datetime(2025, 1, 1, 13, 0, tzinfo=UTC)

    timer = mock_timer_request(
        past_due=True,
        schedule_status={
            "Last": last_run,
            "Next": next_run,
            "LastUpdated": datetime.now(UTC),
        },
        schedule={"Expression": "0 0 * * * *", "AdjustForDST": True},
    )

    assert timer.past_due is True
    assert timer.schedule_status["Last"] == last_run
    assert timer.schedule_status["Next"] == next_run
    assert timer.schedule["Expression"] == "0 0 * * * *"
    assert timer.schedule["AdjustForDST"] is True


def test_mock_timer_request_past_due_with_schedule_info() -> None:
    """Past due timer should have schedule info showing missed execution."""
    now = datetime.now(UTC)
    scheduled_time = now - timedelta(minutes=5)  # Was scheduled 5 minutes ago

    timer = mock_timer_request(
        past_due=True,
        schedule_status={
            "Last": scheduled_time - timedelta(hours=1),
            "Next": scheduled_time,
            "LastUpdated": now,
        },
    )

    assert timer.past_due is True
    assert timer.schedule_status["Next"] < now  # Next run was in the past


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
