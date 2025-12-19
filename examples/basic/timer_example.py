"""Example: Testing Timer triggered Azure Functions."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import json

# Third-party
from azure.functions import Out

# Project/Local
from azure_functions_test import FunctionTestContext, mock_timer_request
from azure_functions_test.protocols import TimerRequestProtocol


# =============================================================================
# EXAMPLE: Simple Timer Function
# =============================================================================
def scheduled_cleanup(timer: TimerRequestProtocol, output: Out[str]) -> None:
    """Perform scheduled cleanup task.

    Args:
        timer: Timer request with scheduling information.
        output: Output binding for cleanup results.
    """
    result = {
        "task": "cleanup",
        "status": "completed",
        "past_due": timer.past_due,
    }

    output.set(json.dumps(result))


def test_scheduled_cleanup_on_time() -> None:
    """Test cleanup function when timer executes on time."""
    # Arrange
    timer = mock_timer_request(past_due=False)
    ctx = FunctionTestContext()

    # Act
    scheduled_cleanup(timer, ctx.out("cleanupResult"))

    # Assert
    result = json.loads(ctx.outputs["cleanupResult"])
    assert result["status"] == "completed"
    assert result["past_due"] is False


def test_scheduled_cleanup_past_due() -> None:
    """Test cleanup function when timer is past due."""
    # Arrange
    timer = mock_timer_request(past_due=True)
    ctx = FunctionTestContext()

    # Act
    scheduled_cleanup(timer, ctx.out("cleanupResult"))

    # Assert
    result = json.loads(ctx.outputs["cleanupResult"])
    assert result["past_due"] is True


# =============================================================================
# EXAMPLE: Timer with Retry Logic
# =============================================================================
def process_daily_report(
    timer: TimerRequestProtocol, warning: Out[str], report: Out[str]
) -> None:
    """Generate and send daily report.

    Args:
        timer: Timer request with scheduling information.
        warning: Output binding for warnings.
        report: Output binding for report data.
    """
    if timer.past_due:
        # Log warning for delayed execution
        warning.set(
            json.dumps(
                {
                    "message": "Timer execution was delayed",
                    "action": "report_generated_with_delay",
                }
            )
        )

    # Generate report
    report_data = {
        "report_type": "daily",
        "generated_at": "2025-01-15T08:00:00Z",
        "delayed": timer.past_due,
    }

    report.set(json.dumps(report_data))


def test_daily_report_on_time() -> None:
    """Test daily report generation when timer executes on time."""
    # Arrange
    timer = mock_timer_request(past_due=False)
    ctx = FunctionTestContext()

    # Act
    process_daily_report(timer, ctx.out("warning"), ctx.out("report"))

    # Assert
    report_data = json.loads(ctx.outputs["report"])
    assert report_data["report_type"] == "daily"
    assert report_data["delayed"] is False


def test_daily_report_delayed() -> None:
    """Test daily report generation when timer is delayed."""
    # Arrange
    timer = mock_timer_request(past_due=True)
    ctx = FunctionTestContext()

    # Act
    process_daily_report(timer, ctx.out("warning"), ctx.out("report"))

    # Assert
    report_data = json.loads(ctx.outputs["report"])
    assert report_data["delayed"] is True

    warning_data = json.loads(ctx.outputs["warning"])
    assert "delayed" in warning_data["message"]


# =============================================================================
# EXAMPLE: Conditional Logic Based on Timer Status
# =============================================================================
def smart_batch_processor(timer: TimerRequestProtocol, output: Out[str]) -> None:
    """Process batches with different strategies based on timing.

    Args:
        timer: Timer request with scheduling information.
        output: Output binding for processing results.
    """
    if timer.past_due:
        # Use fast processing for delayed timers
        strategy = "fast"
        batch_size = 1000
    else:
        # Use thorough processing for on-time timers
        strategy = "thorough"
        batch_size = 100

    result = {
        "strategy": strategy,
        "batch_size": batch_size,
        "on_time": not timer.past_due,
    }

    output.set(json.dumps(result))


def test_batch_processor_on_time_uses_thorough_strategy() -> None:
    """Test that on-time execution uses thorough processing."""
    # Arrange
    timer = mock_timer_request(past_due=False)
    ctx = FunctionTestContext()

    # Act
    smart_batch_processor(timer, ctx.out("processingResult"))

    # Assert
    result = json.loads(ctx.outputs["processingResult"])
    assert result["strategy"] == "thorough"
    assert result["batch_size"] == 100


def test_batch_processor_delayed_uses_fast_strategy() -> None:
    """Test that delayed execution uses fast processing."""
    # Arrange
    timer = mock_timer_request(past_due=True)
    ctx = FunctionTestContext()

    # Act
    smart_batch_processor(timer, ctx.out("processingResult"))

    # Assert
    result = json.loads(ctx.outputs["processingResult"])
    assert result["strategy"] == "fast"
    assert result["batch_size"] == 1000


# =============================================================================
# EXAMPLE: Testing Default Timer Behavior
# =============================================================================
def test_timer_default_is_not_past_due() -> None:
    """Test that timer is not past due by default."""
    # Arrange
    timer = mock_timer_request()

    # Assert
    assert timer.past_due is False


if __name__ == "__main__":
    # Run all test examples
    test_scheduled_cleanup_on_time()
    test_scheduled_cleanup_past_due()
    test_daily_report_on_time()
    test_daily_report_delayed()
    test_batch_processor_on_time_uses_thorough_strategy()
    test_batch_processor_delayed_uses_fast_strategy()
    test_timer_default_is_not_past_due()
    print("✓ All timer request examples passed!")
