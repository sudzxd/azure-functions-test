"""Base utilities for mock implementations.

This module is reserved for future shared mock functionality.
Currently, all mocks use Pydantic dataclasses directly for simplicity
and type safety.
"""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Project/Local
from .._internal import get_logger

# =============================================================================
# MODULE-LEVEL LOGGER
# =============================================================================
logger = get_logger(__name__)

# =============================================================================
# PUBLIC API
# =============================================================================
# (No public exports - reserved for future use)

__all__: list[str] = []
