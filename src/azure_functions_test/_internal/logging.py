"""Centralized logging for azure-functions-test library."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import logging
import sys
from typing import Any

# =============================================================================
# TYPES & CONSTANTS
# =============================================================================
DEFAULT_LOG_LEVEL = logging.WARNING
DEFAULT_FORMAT = "[%(levelname)s] %(name)s: %(message)s"
VERBOSE_FORMAT = (
    "%(asctime)s - [%(levelname)s] - %(name)s - %(funcName)s:%(lineno)d - %(message)s"
)

_loggers: dict[str, logging.Logger] = {}
_configured = False

# =============================================================================
# PUBLIC API
# =============================================================================


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module.

    This function provides centralized logging configuration for the entire
    library. Loggers are cached and reused across the application.

    Args:
        name: The name of the logger (typically __name__).

    Returns:
        A configured logger instance.

    Example:
        >>> from azure_functions_test._internal import get_logger
        >>>
        >>> logger = get_logger(__name__)
        >>> logger.debug("Mock object created")
        >>> logger.info("Test context initialized")
        >>> logger.warning("Output binding not set")
        >>> logger.error("Mock build failed")
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)

    # Configure root logger on first use
    if not _configured:
        _configure_root_logger()

    _loggers[name] = logger
    return logger


def configure_logging(
    level: int = DEFAULT_LOG_LEVEL,
    *,
    format_string: str | None = None,
    verbose: bool = False,
) -> None:
    """Configure library-wide logging settings.

    This function allows users to customize logging behavior for the entire
    azure-functions-test library. It should be called once at the start of
    the test session.

    Args:
        level: The logging level (e.g., logging.DEBUG, logging.INFO).
        format_string: Custom log format string. If None, uses default.
        verbose: If True, uses verbose format with timestamps and line numbers.

    Example:
        >>> import logging
        >>> from azure_functions_test._internal import configure_logging
        >>>
        >>> # Enable debug logging
        >>> configure_logging(level=logging.DEBUG)
        >>>
        >>> # Verbose logging for troubleshooting
        >>> configure_logging(level=logging.DEBUG, verbose=True)
    """
    global _configured  # noqa: PLW0603

    if format_string is None:
        format_string = VERBOSE_FORMAT if verbose else DEFAULT_FORMAT

    # Configure root logger for azure_functions_test
    root_logger = logging.getLogger("azure_functions_test")
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(format_string))
    root_logger.addHandler(handler)

    _configured = True


# =============================================================================
# PRIVATE HELPERS
# =============================================================================


def _configure_root_logger() -> None:
    """Configure the root logger with default settings.

    This is called automatically on first logger creation. Users can override
    these settings by calling configure_logging() explicitly.
    """
    configure_logging(level=DEFAULT_LOG_LEVEL)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def enable_debug_logging() -> None:
    """Enable debug logging for the entire library.

    This is a convenience function for quick debugging during test development.

    Example:
        >>> from azure_functions_test._internal import enable_debug_logging
        >>>
        >>> enable_debug_logging()
        >>> # Now all library logs at DEBUG level and above will be shown
    """
    configure_logging(level=logging.DEBUG, verbose=True)


def disable_logging() -> None:
    """Disable all logging output from the library.

    This is useful for test suites where library logs would be noise.

    Example:
        >>> from azure_functions_test._internal import disable_logging
        >>>
        >>> disable_logging()
        >>> # Now library logs are suppressed
    """
    configure_logging(level=logging.CRITICAL + 1)


def reset_logging() -> None:
    """Reset logging to default settings.

    This clears all configured handlers and resets to library defaults.
    Useful in test teardown.

    Example:
        >>> from azure_functions_test._internal import reset_logging
        >>>
        >>> # After tests
        >>> reset_logging()
    """
    global _configured, _loggers  # noqa: PLW0603

    # Clear all cached loggers
    for logger in _loggers.values():
        logger.handlers.clear()
    _loggers.clear()

    # Reset root logger
    root_logger = logging.getLogger("azure_functions_test")
    root_logger.handlers.clear()
    root_logger.setLevel(logging.NOTSET)

    _configured = False


# =============================================================================
# STRUCTURED LOGGING HELPERS
# =============================================================================


def log_mock_creation(logger: logging.Logger, mock_type: str, **kwargs: Any) -> None:
    """Log mock object creation with structured data.

    Args:
        logger: Logger instance to use.
        mock_type: Type of mock being created (e.g., "QueueMessage").
        **kwargs: Additional context to log.

    Example:
        >>> logger = get_logger(__name__)
        >>> log_mock_creation(logger, "QueueMessage", body={"order_id": 123})
    """
    context = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    logger.debug(f"Creating {mock_type} mock: {context}")


def log_output_capture(logger: logging.Logger, output_name: str, is_set: bool) -> None:
    """Log output binding capture events.

    Args:
        logger: Logger instance to use.
        output_name: Name of the output binding.
        is_set: Whether the output was set.

    Example:
        >>> logger = get_logger(__name__)
        >>> log_output_capture(logger, "result", True)
    """
    status = "set" if is_set else "not set"
    logger.debug(f"Output binding '{output_name}' {status}")
