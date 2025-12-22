"""Timer request mock implementation.

This module provides a duck-typed mock for Azure Timer trigger requests
with Pydantic validation and full type safety.
"""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from datetime import UTC, datetime
from typing import Any

# Third-party
from pydantic import Field
from pydantic.dataclasses import dataclass

# Project/Local
from .._internal import get_logger
from ..protocols import TimerRequestProtocol
from .base import filter_none

# =============================================================================
# LOGGER
# =============================================================================
logger = get_logger(__name__)


# =============================================================================
# CORE CLASSES
# =============================================================================
@dataclass
class TimerRequestMock:
    """Duck-typed mock for Azure Timer trigger requests.

    This class implements the TimerRequestProtocol interface using Pydantic
    dataclass for validation and type safety. It provides schedule information
    and past-due detection for testing timer-triggered functions.

    Attributes:
        past_due: Whether the timer is past its scheduled time. Defaults to False.
        schedule_status: Schedule status with last/next occurrences.
            Defaults to current time info.
        schedule: Timer schedule configuration. Defaults to empty dict.

    Examples:
        Create a timer that's on time:

        >>> timer = TimerRequestMock(past_due=False)
        >>> timer.past_due
        False

        Create a timer that's past due:

        >>> timer = TimerRequestMock(past_due=True)
        >>> timer.past_due
        True

        Create a timer with schedule information:

        >>> from datetime import datetime, UTC
        >>> timer = TimerRequestMock(
        ...     schedule_status={
        ...         "Last": datetime(2025, 1, 1, 12, 0, tzinfo=UTC),
        ...         "Next": datetime(2025, 1, 1, 13, 0, tzinfo=UTC)
        ...     }
        ... )
        >>> timer.schedule_status["Last"]
        datetime.datetime(2025, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
    """

    past_due: bool = Field(default=False)
    schedule_status: dict[str, Any] = Field(
        default_factory=lambda: {
            "Last": datetime.now(UTC),
            "Next": datetime.now(UTC),
            "LastUpdated": datetime.now(UTC),
        }
    )
    schedule: dict[str, Any] = Field(default_factory=dict)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation showing past_due status and memory address.

        Examples:
            >>> timer = TimerRequestMock(past_due=True)
            >>> repr(timer)
            "<TimerRequestMock past_due=True at 0x...>"
        """
        return f"<TimerRequestMock past_due={self.past_due} at {hex(id(self))}>"


# =============================================================================
# PUBLIC API
# =============================================================================
def mock_timer_request(
    *,
    past_due: bool = False,
    schedule_status: dict[str, Any] | None = None,
    schedule: dict[str, Any] | None = None,
) -> TimerRequestProtocol:
    """Create a mock TimerRequest for testing.

    Provides a test double for Azure Timer trigger inputs with sensible
    defaults. Returns an object that implements TimerRequestProtocol.

    Args:
        past_due: Whether the timer is past its scheduled time. Defaults to False.
        schedule_status: Schedule status with Last/Next/LastUpdated times.
            Defaults to current time.
        schedule: Timer schedule configuration (e.g., cron expression).
            Defaults to empty dict.

    Returns:
        A TimerRequestMock instance implementing TimerRequestProtocol.

    Examples:
        Create a timer that's on schedule:

        >>> timer = mock_timer_request()
        >>> timer.past_due
        False

        Create a timer that's past due:

        >>> timer = mock_timer_request(past_due=True)
        >>> timer.past_due
        True

        Create a timer with schedule information:

        >>> from datetime import datetime, UTC, timedelta
        >>> now = datetime.now(UTC)
        >>> timer = mock_timer_request(
        ...     schedule_status={
        ...         "Last": now - timedelta(hours=1),
        ...         "Next": now + timedelta(hours=1),
        ...         "LastUpdated": now
        ...     },
        ...     schedule={"AdjustForDST": True}
        ... )
        >>> timer.schedule_status["Last"] < timer.schedule_status["Next"]
        True

        Simulate past-due handling logic:

        >>> timer = mock_timer_request(past_due=True)
        >>> if timer.past_due:
        ...     print("Timer execution was delayed")
        Timer execution was delayed
    """
    logger.debug(
        "Creating TimerRequestMock with past_due=%s, has_schedule_status=%s",
        past_due,
        schedule_status is not None,
    )

    return TimerRequestMock(
        **filter_none(
            past_due=past_due if past_due else None,  # Only pass if True
            schedule_status=schedule_status,
            schedule=schedule,
        )
    )
