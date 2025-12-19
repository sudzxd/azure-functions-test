"""Timer request mock implementation.

This module provides a duck-typed mock for Azure Timer trigger requests
with Pydantic validation and full type safety.
"""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Third-party
from pydantic import Field
from pydantic.dataclasses import dataclass

# Project/Local
from .._internal import get_logger
from ..protocols import TimerRequestProtocol

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
    dataclass for validation and type safety. It provides simple boolean
    flag for past-due detection.

    Attributes:
        past_due: Whether the timer is past its scheduled time. Defaults to False.

    Examples:
        Create a timer that's on time:

        >>> timer = TimerRequestMock(past_due=False)
        >>> timer.past_due
        False

        Create a timer that's past due:

        >>> timer = TimerRequestMock(past_due=True)
        >>> timer.past_due
        True
    """

    past_due: bool = Field(default=False)

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
) -> TimerRequestProtocol:
    """Create a mock TimerRequest for testing.

    Provides a test double for Azure Timer trigger inputs with sensible
    defaults. Returns an object that implements TimerRequestProtocol.

    Args:
        past_due: Whether the timer is past its scheduled time. Defaults to False.

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

        Simulate past-due handling logic:

        >>> timer = mock_timer_request(past_due=True)
        >>> if timer.past_due:
        ...     print("Timer execution was delayed")
        Timer execution was delayed
    """
    logger.debug("Creating TimerRequestMock with past_due=%s", past_due)

    return TimerRequestMock(past_due=past_due)
