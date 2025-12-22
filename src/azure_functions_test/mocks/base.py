"""Base utilities for mock implementations.

This module provides shared utilities and validation helpers used across
all mock implementations for consistency and reusability."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import re
import uuid
from datetime import UTC, datetime
from typing import Any

# Project/Local
from .._internal import get_logger

# =============================================================================
# MODULE-LEVEL LOGGER
# =============================================================================
logger = get_logger(__name__)

# =============================================================================
# VALIDATION HELPERS
# =============================================================================


def validate_azure_storage_name(name: str) -> bool:
    """Validate Azure Storage account/container naming conventions.

    Args:
        name: The storage name to validate.

    Returns:
        True if the name follows Azure Storage naming rules.

    Examples:
        >>> validate_azure_storage_name("mystorageaccount")
        True
        >>> validate_azure_storage_name("MyStorageAccount")
        False
    """
    # Azure Storage naming rules:
    # - 3-24 characters
    # - lowercase letters and numbers only
    # - must start with letter or number
    pattern = r"^[a-z0-9][a-z0-9]{2,23}$"
    return bool(re.match(pattern, name))


def validate_queue_name(name: str) -> bool:
    """Validate Azure Queue Storage naming conventions.

    Args:
        name: The queue name to validate.

    Returns:
        True if the name follows Azure Queue naming rules.

    Examples:
        >>> validate_queue_name("my-queue")
        True
        >>> validate_queue_name("MyQueue")
        False
    """
    # Azure Queue naming rules:
    # - 3-63 characters
    # - lowercase letters, numbers, and hyphens
    # - cannot start or end with hyphen
    # - cannot have consecutive hyphens
    pattern = r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"
    return bool(re.match(pattern, name)) and 3 <= len(name) <= 63


# =============================================================================
# ID GENERATORS
# =============================================================================


def generate_azure_resource_id(resource_type: str, resource_name: str) -> str:
    """Generate realistic Azure resource ID.

    Args:
        resource_type: Type of Azure resource (e.g., 'storageAccounts', 'topics').
        resource_name: Name of the resource.

    Returns:
        Formatted Azure resource ID.

    Examples:
        >>> generate_azure_resource_id("storageAccounts", "mystorageaccount")
        '/subscriptions/.../resourceGroups/.../providers/Microsoft.Storage/storageAccounts/mystorageaccount'
    """
    subscription_id = str(uuid.uuid4())
    resource_group = "test-resource-group"

    provider_mapping = {
        "storageAccounts": "Microsoft.Storage",
        "topics": "Microsoft.EventGrid",
        "namespaces": "Microsoft.ServiceBus",
        "sites": "Microsoft.Web",
    }

    provider = provider_mapping.get(resource_type, "Microsoft.Test")

    return (
        f"/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}"
        f"/providers/{provider}"
        f"/{resource_type}/{resource_name}"
    )


def generate_message_id() -> str:
    """Generate a realistic message ID.

    Returns:
        UUID-based message ID.

    Examples:
        >>> msg_id = generate_message_id()
        >>> len(msg_id)
        36
    """
    return str(uuid.uuid4())


def generate_blob_uri(account_name: str, container_name: str, blob_name: str) -> str:
    """Generate a realistic Azure Blob Storage URI.

    Args:
        account_name: Storage account name.
        container_name: Container name.
        blob_name: Blob name.

    Returns:
        Complete blob URI.

    Examples:
        >>> generate_blob_uri("myaccount", "container", "file.txt")
        'https://myaccount.blob.core.windows.net/container/file.txt'
    """
    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}"


# =============================================================================
# TIME UTILITIES
# =============================================================================


def get_utc_now() -> datetime:
    """Get current UTC datetime.

    Returns:
        Current UTC datetime with timezone info.

        >>> now.tzinfo == UTC
        True
    """
    return datetime.now(UTC)


# =============================================================================
# COMMON MOCK DATA
# =============================================================================

DEFAULT_STORAGE_ACCOUNT = "teststorageaccount"
DEFAULT_CONTAINER_NAME = "test-container"
DEFAULT_QUEUE_NAME = "test-queue"
DEFAULT_TOPIC_NAME = "test-topic"
DEFAULT_SUBSCRIPTION_NAME = "test-subscription"

# =============================================================================
# FACTORY HELPERS
# =============================================================================


def filter_none(**kwargs: Any) -> dict[str, Any]:
    """Filter out None values from kwargs.

    This helper is used by all mock factory functions to allow None parameters
    while letting Pydantic dataclass defaults take effect.

    Args:
        **kwargs: Keyword arguments to filter.

    Returns:
        Dictionary with None values removed.

    Examples:
        >>> filter_none(a=1, b=None, c="test")
        {'a': 1, 'c': 'test'}
    """
    return {k: v for k, v in kwargs.items() if v is not None}


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    "validate_azure_storage_name",
    "validate_queue_name",
    "generate_azure_resource_id",
    "generate_message_id",
    "generate_blob_uri",
    "get_utc_now",
    "filter_none",
    "DEFAULT_STORAGE_ACCOUNT",
    "DEFAULT_CONTAINER_NAME",
    "DEFAULT_QUEUE_NAME",
    "DEFAULT_TOPIC_NAME",
    "DEFAULT_SUBSCRIPTION_NAME",
]
