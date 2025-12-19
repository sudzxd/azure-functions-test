"""Pytest configuration and shared fixtures."""

from __future__ import annotations

from collections.abc import Generator

# =============================================================================
# IMPORTS
# =============================================================================
# Third-party
import pytest

# Project/Local
from azure_functions_test._internal.logging import reset_logging


# =============================================================================
# FIXTURES
# =============================================================================
@pytest.fixture(autouse=True)
def reset_logging_fixture() -> Generator[None, None, None]:
    """Reset logging configuration before each test.

    This ensures tests don't interfere with each other's logging settings.
    """
    reset_logging()
    yield
    reset_logging()
