"""Azure Functions Test - Unit test Azure Functions without the runtime."""

from __future__ import annotations

# ==============================================================================
# IMPORTS
# ==============================================================================
# Project/Local
from .context import CapturedOutput, FunctionTestContext
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
