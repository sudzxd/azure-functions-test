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
    expiration_time: Any = None,
    insertion_time: Any = None,
    time_next_visible: Any = None,
    pop_receipt: str | None = None,
) -> QueueMessageProtocol: ...

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
    event_time: Any = None,
    data_version: str | None = None,
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
    enqueued_time_utc: Any = None,
    expires_at_utc: Any = None,
    dead_letter_source: str | None = None,
    dead_letter_reason: str | None = None,
    dead_letter_error_description: str | None = None,
    application_properties: dict[str, Any] | None = None,
    user_properties: dict[str, Any] | None = None,
) -> ServiceBusMessageProtocol: ...

__all__ = [
    # Context
    "FunctionTestContext",
    "CapturedOutput",
    # Mocks
    "mock_queue_message",
    "mock_http_request",
    "mock_timer_request",
    "mock_blob",
    "mock_event_grid_event",
    "mock_service_bus_message",
]
