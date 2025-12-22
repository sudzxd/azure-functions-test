"""Type stubs for azure_functions_test.

This stub file provides type hints using our Protocol types which have full
type annotations, providing a better developer experience than the Azure SDK types.

Our mocks are structurally compatible with Azure SDK types (duck typing) but
provide complete type information.
"""

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from datetime import datetime, timedelta
from typing import Any

# Project/local
from .context import CapturedOutput as CapturedOutput
from .context import FunctionTestContext as FunctionTestContext
from .protocols import (
    EventGridEventProtocol,
    HttpRequestProtocol,
    InputStreamProtocol,
    QueueMessageProtocol,
    ServiceBusMessageProtocol,
    TimerRequestProtocol,
)

# =============================================================================
# Queue Mock
# =============================================================================
def mock_queue_message(
    body: dict[Any, Any] | list[Any] | str | bytes | None = None,
    *,
    id: str | None = None,
    dequeue_count: int | None = None,
    expiration_time: datetime | None = None,
    insertion_time: datetime | None = None,
    time_next_visible: datetime | None = None,
    pop_receipt: str | None = None,
) -> QueueMessageProtocol: ...
def create_poison_message(
    body: dict[Any, Any] | list[Any] | str | bytes | None = None,
    *,
    dequeue_count: int = 6,
    **kwargs: Any,
) -> QueueMessageProtocol: ...
def create_batch_messages(
    bodies: list[dict[Any, Any] | list[Any] | str | bytes],
    **kwargs: Any,
) -> list[QueueMessageProtocol]: ...

# =============================================================================
# HTTP Mock
# =============================================================================
def mock_http_request(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    method: str = "GET",
    url: str = "http://localhost",
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    route_params: dict[str, str] | None = None,
) -> HttpRequestProtocol: ...

# =============================================================================
# Timer Mock
# =============================================================================
def mock_timer_request(
    *,
    past_due: bool = False,
    schedule_status: dict[str, Any] | None = None,
    schedule: dict[str, Any] | None = None,
) -> TimerRequestProtocol: ...

# =============================================================================
# Blob Mock
# =============================================================================
def mock_blob(
    content: str | bytes | None = None,
    *,
    name: str | None = None,
    uri: str | None = None,
) -> InputStreamProtocol: ...

# =============================================================================
# Event Grid Mock
# =============================================================================
def mock_event_grid_event(
    *,
    data: dict[str, Any] | None = None,
    id: str | None = None,
    topic: str | None = None,
    subject: str | None = None,
    event_type: str | None = None,
    event_time: datetime | None = None,
    data_version: str | None = None,
) -> EventGridEventProtocol: ...
def create_blob_created_event(
    blob_url: str,
    *,
    container_name: str = "test-container",
    blob_name: str | None = None,
    storage_account: str = "teststorageaccount",
    **kwargs: Any,
) -> EventGridEventProtocol: ...
def create_blob_deleted_event(
    blob_url: str,
    *,
    container_name: str = "test-container",
    blob_name: str | None = None,
    storage_account: str = "teststorageaccount",
    **kwargs: Any,
) -> EventGridEventProtocol: ...
def create_custom_event(
    data: dict[str, Any],
    *,
    event_type: str = "Custom.Application.Event",
    subject: str = "custom/event",
    **kwargs: Any,
) -> EventGridEventProtocol: ...

# =============================================================================
# Service Bus Mock
# =============================================================================
def mock_service_bus_message(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    message_id: str | None = None,
    session_id: str | None = None,
    partition_key: str | None = None,
    content_type: str | None = None,
    correlation_id: str | None = None,
    delivery_count: int | None = None,
    enqueued_time_utc: datetime | None = None,
    expires_at_utc: datetime | None = None,
    expiration_time: datetime | None = None,
    dead_letter_source: str | None = None,
    dead_letter_reason: str | None = None,
    dead_letter_error_description: str | None = None,
    locked_until: datetime | None = None,
    lock_token: str | None = None,
    sequence_number: int | None = None,
    enqueued_sequence_number: int | None = None,
    scheduled_enqueue_time: datetime | None = None,
    scheduled_enqueue_time_utc: datetime | None = None,
    label: str | None = None,
    subject: str | None = None,
    reply_to: str | None = None,
    reply_to_session_id: str | None = None,
    to: str | None = None,
    time_to_live: timedelta | None = None,
    state: int | None = None,
    transaction_partition_key: str | None = None,
    application_properties: dict[str, Any] | None = None,
    user_properties: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> ServiceBusMessageProtocol: ...
def create_session_message(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    session_id: str = "default-session",
    partition_key: str | None = None,
    **kwargs: Any,
) -> ServiceBusMessageProtocol: ...
def create_dead_letter_message(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    reason: str = "ProcessingError",
    description: str = "Message processing failed after maximum retries",
    source: str = "original-queue",
    delivery_count: int = 10,
    **kwargs: Any,
) -> ServiceBusMessageProtocol: ...
def create_scheduled_message(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    scheduled_time: datetime | None = None,
    **kwargs: Any,
) -> ServiceBusMessageProtocol: ...
def create_request_reply_message(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    correlation_id: str | None = None,
    reply_to: str = "response-queue",
    **kwargs: Any,
) -> ServiceBusMessageProtocol: ...

__all__ = [
    # Context
    "FunctionTestContext",
    "CapturedOutput",
    # Base Mocks
    "mock_queue_message",
    "mock_http_request",
    "mock_timer_request",
    "mock_blob",
    "mock_event_grid_event",
    "mock_service_bus_message",
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
