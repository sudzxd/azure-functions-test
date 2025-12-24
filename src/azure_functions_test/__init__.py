"""Azure Functions Test - Unit test Azure Functions without the runtime."""

from __future__ import annotations

# ==============================================================================
# IMPORTS
# ==============================================================================
# Project/Local
from .constants import (
    BATCH_MESSAGE_ID_PREFIX,
    CUSTOM_EVENT_SUBJECT,
    CUSTOM_EVENT_TYPE,
    DEFAULT_BLOB_CONTENT_LENGTH,
    DEFAULT_BLOB_NAME,
    DEFAULT_BLOB_URI,
    DEFAULT_CONTAINER_NAME,
    DEFAULT_EVENT_DATA_VERSION,
    DEFAULT_EVENT_ID,
    DEFAULT_EVENT_TOPIC,
    DEFAULT_HTTP_METHOD,
    DEFAULT_HTTP_URL,
    DEFAULT_MESSAGE_ID,
    DEFAULT_POP_RECEIPT,
    DEFAULT_QUEUE_NAME,
    DEFAULT_RESOURCE_GROUP,
    DEFAULT_STORAGE_ACCOUNT,
    DEFAULT_SUBSCRIPTION_NAME,
    DEFAULT_TOPIC_NAME,
    DEQUEUE_COUNT_DEFAULT,
    DEQUEUE_COUNT_POISON_EXAMPLE,
    DEQUEUE_COUNT_POISON_THRESHOLD,
    QUEUE_NAME_MAX_LENGTH,
    QUEUE_NAME_MIN_LENGTH,
    QUEUE_NAME_PATTERN,
    SERVICE_BUS_DELIVERY_COUNT_DEFAULT,
    STORAGE_ACCOUNT_NAME_MAX_LENGTH,
    STORAGE_ACCOUNT_NAME_MIN_LENGTH,
    STORAGE_ACCOUNT_NAME_PATTERN,
)
from .context import CapturedOutput, FunctionTestContext
from .enums import (
    AzureProvider,
    BlobOperation,
    BlobType,
    ContentType,
    EventGridEventType,
    HttpMethod,
    ScheduleStatusKey,
)
from .mocks.blob import mock_blob
from .mocks.eventgrid import (
    create_blob_created_event,
    create_blob_deleted_event,
    create_custom_event,
    mock_event_grid_event,
)
from .mocks.http import mock_http_request
from .mocks.queue import (
    create_batch_messages,
    create_poison_message,
    mock_queue_message,
)
from .mocks.servicebus import (
    create_dead_letter_message,
    create_request_reply_message,
    create_scheduled_message,
    create_session_message,
    mock_service_bus_message,
)
from .mocks.timer import mock_timer_request

# ==============================================================================
# PUBLIC API
# ==============================================================================
__all__ = [
    # Enums
    "HttpMethod",
    "ContentType",
    "AzureProvider",
    "EventGridEventType",
    "BlobOperation",
    "BlobType",
    "ScheduleStatusKey",
    # Constants - Default Values
    "DEFAULT_HTTP_METHOD",
    "DEFAULT_HTTP_URL",
    "DEFAULT_MESSAGE_ID",
    "DEFAULT_POP_RECEIPT",
    "DEFAULT_BLOB_NAME",
    "DEFAULT_BLOB_URI",
    "DEFAULT_CONTAINER_NAME",
    "DEFAULT_QUEUE_NAME",
    "DEFAULT_TOPIC_NAME",
    "DEFAULT_SUBSCRIPTION_NAME",
    "DEFAULT_STORAGE_ACCOUNT",
    "DEFAULT_RESOURCE_GROUP",
    "DEFAULT_EVENT_ID",
    "DEFAULT_EVENT_TOPIC",
    "DEFAULT_EVENT_DATA_VERSION",
    "DEFAULT_BLOB_CONTENT_LENGTH",
    "CUSTOM_EVENT_TYPE",
    "CUSTOM_EVENT_SUBJECT",
    # Constants - Magic Numbers
    "DEQUEUE_COUNT_DEFAULT",
    "DEQUEUE_COUNT_POISON_THRESHOLD",
    "DEQUEUE_COUNT_POISON_EXAMPLE",
    "SERVICE_BUS_DELIVERY_COUNT_DEFAULT",
    "BATCH_MESSAGE_ID_PREFIX",
    # Constants - Validation
    "STORAGE_ACCOUNT_NAME_MIN_LENGTH",
    "STORAGE_ACCOUNT_NAME_MAX_LENGTH",
    "STORAGE_ACCOUNT_NAME_PATTERN",
    "QUEUE_NAME_MIN_LENGTH",
    "QUEUE_NAME_MAX_LENGTH",
    "QUEUE_NAME_PATTERN",
    # Context
    "FunctionTestContext",
    "CapturedOutput",
    # Base Mocks
    "mock_blob",
    "mock_event_grid_event",
    "mock_queue_message",
    "mock_http_request",
    "mock_service_bus_message",
    "mock_timer_request",
    # Factory Functions - Queue
    "create_poison_message",
    "create_batch_messages",
    # Factory Functions - Event Grid
    "create_blob_created_event",
    "create_blob_deleted_event",
    "create_custom_event",
    # Factory Functions - Service Bus
    "create_session_message",
    "create_dead_letter_message",
    "create_scheduled_message",
    "create_request_reply_message",
]
