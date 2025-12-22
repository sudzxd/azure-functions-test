"""Mock implementations for Azure Functions triggers."""

from __future__ import annotations

# Re-export all factory functions and base mocks
from .blob import mock_blob
from .eventgrid import (
    create_blob_created_event,
    create_blob_deleted_event,
    create_custom_event,
    mock_event_grid_event,
)
from .http import mock_http_request
from .queue import create_batch_messages, create_poison_message, mock_queue_message
from .servicebus import (
    create_dead_letter_message,
    create_request_reply_message,
    create_scheduled_message,
    create_session_message,
    mock_service_bus_message,
)
from .timer import mock_timer_request

__all__ = [
    # Base mocks
    "mock_blob",
    "mock_event_grid_event",
    "mock_http_request",
    "mock_queue_message",
    "mock_service_bus_message",
    "mock_timer_request",
    # Factory functions - Queue
    "create_poison_message",
    "create_batch_messages",
    # Factory functions - Event Grid
    "create_blob_created_event",
    "create_blob_deleted_event",
    "create_custom_event",
    # Factory functions - Service Bus
    "create_session_message",
    "create_dead_letter_message",
    "create_scheduled_message",
    "create_request_reply_message",
]
