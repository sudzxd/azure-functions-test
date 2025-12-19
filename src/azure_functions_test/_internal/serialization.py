"""Shared serialization utilities for mock implementations."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import json
from typing import Any

# =============================================================================
# PUBLIC API
# =============================================================================


def serialize_to_bytes(
    data: dict[Any, Any] | list[Any] | str | bytes | None,
    *,
    allow_list: bool = True,
) -> bytes:
    """Serialize data to bytes for Azure Functions mock bodies.

    Provides consistent serialization across all mock types with automatic
    JSON encoding for structured data.

    Args:
        data: Data to serialize. Accepts:
            - dict: JSON-serialized to UTF-8 bytes
            - list: JSON-serialized to UTF-8 bytes (if allow_list=True)
            - str: UTF-8 encoded to bytes
            - bytes: Returned as-is
            - None: Returns empty bytes
        allow_list: Whether to allow list serialization. Defaults to True.

    Returns:
        Serialized data as bytes.

    Raises:
        TypeError: If data type is not supported or list when allow_list=False.

    Examples:
        >>> serialize_to_bytes({"key": "value"})
        b'{"key": "value"}'

        >>> serialize_to_bytes("Hello")
        b'Hello'

        >>> serialize_to_bytes([1, 2, 3])
        b'[1, 2, 3]'

        >>> serialize_to_bytes(None)
        b''
    """
    if data is None:
        return b""
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode("utf-8")
    if isinstance(data, dict):
        return json.dumps(data).encode("utf-8")
    # Type narrowing: must be list[Any] at this point
    if not allow_list:
        msg = "List serialization not allowed for this mock type"
        raise TypeError(msg)
    return json.dumps(data).encode("utf-8")
