"""Constants for azure-functions-test.

This module provides centralized constants for default values, magic numbers,
and other configuration used throughout the test framework.
"""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
from datetime import timedelta

# =============================================================================
# DEFAULT TEST VALUES - IDs and Names
# =============================================================================

# Message and event identifiers
DEFAULT_MESSAGE_ID = "test-message-id"
DEFAULT_EVENT_ID = "test-event-id"
DEFAULT_POP_RECEIPT = "test-pop-receipt"
DEFAULT_SESSION_ID = "default-session"

# Resource names
DEFAULT_STORAGE_ACCOUNT = "teststorageaccount"
DEFAULT_CONTAINER_NAME = "test-container"
DEFAULT_QUEUE_NAME = "test-queue"
DEFAULT_TOPIC_NAME = "test-topic"
DEFAULT_SUBSCRIPTION_NAME = "test-subscription"
DEFAULT_RESOURCE_GROUP = "test-resource-group"

# Queue name validation pattern
QUEUE_NAME_PATTERN = r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"

# Blob names and URIs
DEFAULT_BLOB_NAME = "test-blob.txt"
DEFAULT_BLOB_URI = "https://test.blob.core.windows.net/container/test-blob.txt"

# HTTP defaults
DEFAULT_HTTP_METHOD = "GET"
DEFAULT_HTTP_URL = "http://localhost"

# Event Grid defaults
DEFAULT_EVENT_TYPE = "Test.Event"
DEFAULT_EVENT_TOPIC = (
    "/subscriptions/sub-id/resourceGroups/rg/"
    "providers/Microsoft.EventGrid/topics/test-topic"
)
DEFAULT_EVENT_DATA_VERSION = "1.0"

# Custom event defaults
CUSTOM_EVENT_TYPE = "Custom.Application.Event"
CUSTOM_EVENT_SUBJECT = "custom/event"

# Service Bus defaults
DEFAULT_REPLY_TO_QUEUE = "response-queue"
DEFAULT_DEAD_LETTER_SOURCE = "original-queue"
DEFAULT_DEAD_LETTER_REASON = "ProcessingError"
DEFAULT_DEAD_LETTER_DESCRIPTION = "Message processing failed after maximum retries"

# Batch operation prefix
BATCH_MESSAGE_ID_PREFIX = "batch-message"

# =============================================================================
# MAGIC NUMBERS - Thresholds and Limits
# =============================================================================

# Queue message thresholds
DEQUEUE_COUNT_DEFAULT = 1
DEQUEUE_COUNT_POISON_THRESHOLD = 5
DEQUEUE_COUNT_POISON_EXAMPLE = 6  # Used in examples/tests

# Service Bus delivery count
SERVICE_BUS_DELIVERY_COUNT_DEFAULT = 10

# Content lengths
DEFAULT_BLOB_CONTENT_LENGTH = 1024

# String length validation ranges
STORAGE_ACCOUNT_NAME_MIN_LENGTH = 3
STORAGE_ACCOUNT_NAME_MAX_LENGTH = 24
QUEUE_NAME_MIN_LENGTH = 3
QUEUE_NAME_MAX_LENGTH = 63

# UUID hex length for ETags
ETAG_HEX_LENGTH = 16

# =============================================================================
# TIME DURATIONS
# =============================================================================

# Service Bus time offsets
SERVICE_BUS_SCHEDULED_TIME_OFFSET = timedelta(hours=1)
SERVICE_BUS_SCHEDULED_TIME_OFFSET_LONG = timedelta(hours=2)
SERVICE_BUS_LOCK_TIMEOUT = timedelta(minutes=5)

# =============================================================================
# URI PATTERNS
# =============================================================================

# Azure Blob Storage URI pattern
BLOB_URI_PATTERN = "https://{account}.blob.core.windows.net/{container}/{blob}"

# =============================================================================
# TIMESTAMP FORMATS
# =============================================================================

# Event Grid timestamp format (used in blob events)
EVENT_GRID_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
EVENT_GRID_TIMESTAMP_SUFFIX = "0000000000000"

# =============================================================================
# VALIDATION PATTERNS
# =============================================================================

# Storage account name validation (3-24 lowercase alphanumeric)
STORAGE_ACCOUNT_NAME_PATTERN = r"^[a-z0-9][a-z0-9]{2,23}$"

# =============================================================================
# PROVIDER MAPPINGS
# =============================================================================

# Map resource types to Azure providers
RESOURCE_TYPE_TO_PROVIDER = {
    "storageAccounts": "Microsoft.Storage",
    "topics": "Microsoft.EventGrid",
    "namespaces": "Microsoft.ServiceBus",
    "sites": "Microsoft.Web",
}

DEFAULT_PROVIDER = "Microsoft.Test"
