"""Example: Testing Service Bus triggered Azure Functions."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import json
from datetime import UTC, datetime

# Third-party
from azure.functions import Out

# Project/Local
from azure_functions_test import FunctionTestContext, mock_service_bus_message
from azure_functions_test.protocols import ServiceBusMessageProtocol


# =============================================================================
# EXAMPLE: Simple Message Processing
# =============================================================================
def process_order_message(msg: ServiceBusMessageProtocol, output: Out[str]) -> None:
    """Process order message from Service Bus.

    Args:
        msg: Service Bus message with order data.
        output: Output binding for processed results.
    """
    order_data = json.loads(msg.get_body().decode("utf-8"))

    result = {
        "message_id": msg.message_id,
        "order_id": order_data.get("order_id"),
        "status": "processed",
    }

    output.set(json.dumps(result))


def test_process_order_message() -> None:
    """Test basic Service Bus message processing."""
    # Arrange
    order_data = {"order_id": "ORD-123", "items": ["item1", "item2"], "total": 99.99}
    msg = mock_service_bus_message(order_data)
    ctx = FunctionTestContext()

    # Act
    process_order_message(msg, ctx.out("processedOrder"))

    # Assert
    result = json.loads(ctx.outputs["processedOrder"])
    assert result["order_id"] == "ORD-123"
    assert result["status"] == "processed"


# =============================================================================
# EXAMPLE: Session-Based Processing
# =============================================================================
def process_session_message(msg: ServiceBusMessageProtocol, output: Out[str]) -> None:
    """Process message from session-enabled queue.

    Args:
        msg: Service Bus message with session ID.
        output: Output binding for processing results.
    """
    data = json.loads(msg.get_body().decode("utf-8"))

    result = {
        "session_id": msg.session_id,
        "message_id": msg.message_id,
        "data": data,
    }

    output.set(json.dumps(result))


def test_process_session_message() -> None:
    """Test Service Bus message with session support."""
    # Arrange
    msg = mock_service_bus_message(
        {"action": "update", "value": 42},
        session_id="session-123",
        message_id="msg-456",
    )
    ctx = FunctionTestContext()

    # Act
    process_session_message(msg, ctx.out("sessionResult"))

    # Assert
    result = json.loads(ctx.outputs["sessionResult"])
    assert result["session_id"] == "session-123"
    assert result["message_id"] == "msg-456"


# =============================================================================
# EXAMPLE: Retry Logic with Delivery Count
# =============================================================================
def process_with_retry_logic(
    msg: ServiceBusMessageProtocol, dead_letter: Out[str], processed: Out[str]
) -> None:
    """Process message with retry logic based on delivery count.

    Args:
        msg: Service Bus message with delivery tracking.
        dead_letter: Output binding for dead letter queue.
        processed: Output binding for processed messages.
    """
    max_retries = 3

    if msg.delivery_count > max_retries:
        # Move to dead letter queue
        dead_letter.set(
            json.dumps(
                {
                    "message_id": msg.message_id,
                    "reason": "MaxDeliveryCountExceeded",
                    "delivery_count": msg.delivery_count,
                }
            )
        )
        return

    # Normal processing
    data = json.loads(msg.get_body().decode("utf-8"))
    processed.set(json.dumps(data))


def test_process_with_max_retries_exceeded() -> None:
    """Test message processing when max retries exceeded."""
    # Arrange
    msg = mock_service_bus_message({"data": "test"}, delivery_count=4)
    ctx = FunctionTestContext()

    # Act
    process_with_retry_logic(msg, ctx.out("deadLetter"), ctx.out("processed"))

    # Assert
    dead_letter_data = json.loads(ctx.outputs["deadLetter"])
    assert dead_letter_data["reason"] == "MaxDeliveryCountExceeded"
    assert dead_letter_data["delivery_count"] == 4


def test_process_within_retry_limit() -> None:
    """Test message processing within retry limit."""
    # Arrange
    msg = mock_service_bus_message({"data": "test"}, delivery_count=2)
    ctx = FunctionTestContext()

    # Act
    process_with_retry_logic(msg, ctx.out("deadLetter"), ctx.out("processed"))

    # Assert
    processed_data = json.loads(ctx.outputs["processed"])
    assert processed_data["data"] == "test"


# =============================================================================
# EXAMPLE: Application Properties
# =============================================================================
def process_priority_message(msg: ServiceBusMessageProtocol, output: Out[str]) -> None:
    """Process message with priority from application properties.

    Args:
        msg: Service Bus message with application properties.
        output: Output binding for processing results.
    """
    priority = msg.application_properties.get("priority", "normal")

    result = {
        "message_id": msg.message_id,
        "priority": priority,
        "processing_queue": "high-priority" if priority == "high" else "normal",
    }

    output.set(json.dumps(result))


def test_process_high_priority_message() -> None:
    """Test processing high priority message."""
    # Arrange
    msg = mock_service_bus_message(
        {"data": "urgent"},
        application_properties={"priority": "high", "version": "1.0"},
    )
    ctx = FunctionTestContext()

    # Act
    process_priority_message(msg, ctx.out("priorityResult"))

    # Assert
    result = json.loads(ctx.outputs["priorityResult"])
    assert result["priority"] == "high"
    assert result["processing_queue"] == "high-priority"


# =============================================================================
# EXAMPLE: Dead Letter Queue Processing
# =============================================================================
def process_dead_letter_message(
    msg: ServiceBusMessageProtocol, output: Out[str]
) -> None:
    """Process message from dead letter queue.

    Args:
        msg: Dead lettered Service Bus message.
        output: Output binding for analysis results.
    """
    result = {
        "message_id": msg.message_id,
        "dead_letter_source": msg.dead_letter_source,
        "dead_letter_reason": msg.dead_letter_reason,
        "dead_letter_description": msg.dead_letter_error_description,
        "delivery_count": msg.delivery_count,
    }

    output.set(json.dumps(result))


def test_process_dead_letter_message() -> None:
    """Test processing message from dead letter queue."""
    # Arrange
    msg = mock_service_bus_message(
        "failed message",
        message_id="msg-789",
        dead_letter_source="orders-queue",
        dead_letter_reason="ValidationError",
        dead_letter_error_description="Invalid order data format",
        delivery_count=10,
    )
    ctx = FunctionTestContext()

    # Act
    process_dead_letter_message(msg, ctx.out("deadLetterAnalysis"))

    # Assert
    result = json.loads(ctx.outputs["deadLetterAnalysis"])
    assert result["dead_letter_source"] == "orders-queue"
    assert result["dead_letter_reason"] == "ValidationError"
    assert result["delivery_count"] == 10


# =============================================================================
# EXAMPLE: Message Correlation
# =============================================================================
def process_correlated_message(
    msg: ServiceBusMessageProtocol, output: Out[str]
) -> None:
    """Process message with correlation tracking.

    Args:
        msg: Service Bus message with correlation ID.
        output: Output binding for processing results.
    """
    result = {
        "message_id": msg.message_id,
        "correlation_id": msg.correlation_id,
        "content_type": msg.content_type,
    }

    output.set(json.dumps(result))


def test_process_correlated_message() -> None:
    """Test message processing with correlation ID."""
    # Arrange
    msg = mock_service_bus_message(
        {"data": "test"},
        message_id="msg-123",
        correlation_id="corr-456",
        content_type="application/json",
    )
    ctx = FunctionTestContext()

    # Act
    process_correlated_message(msg, ctx.out("correlationResult"))

    # Assert
    result = json.loads(ctx.outputs["correlationResult"])
    assert result["message_id"] == "msg-123"
    assert result["correlation_id"] == "corr-456"
    assert result["content_type"] == "application/json"


# =============================================================================
# EXAMPLE: User Properties
# =============================================================================
def test_message_with_user_properties() -> None:
    """Test Service Bus message with user properties."""
    # Arrange
    msg = mock_service_bus_message(
        {"data": "test"},
        user_properties={"source": "api", "user_id": 123, "tenant": "tenant-abc"},
    )

    # Assert
    assert msg.user_properties["source"] == "api"
    assert msg.user_properties["user_id"] == 123
    assert msg.user_properties["tenant"] == "tenant-abc"


# =============================================================================
# EXAMPLE: Message Timing
# =============================================================================
def test_message_with_timing_metadata() -> None:
    """Test Service Bus message with timing information."""
    # Arrange
    enqueued_time = datetime(2025, 1, 15, 10, 0, 0, tzinfo=UTC)
    expires_at = datetime(2025, 1, 16, 10, 0, 0, tzinfo=UTC)

    msg = mock_service_bus_message(
        {"data": "test"},
        enqueued_time_utc=enqueued_time,
        expires_at_utc=expires_at,
    )

    # Assert
    assert msg.enqueued_time_utc == enqueued_time
    assert msg.expires_at_utc == expires_at


# =============================================================================
# EXAMPLE: Different Body Types
# =============================================================================
def test_message_with_string_body() -> None:
    """Test Service Bus message with string body."""
    # Arrange
    msg = mock_service_bus_message("Hello, Service Bus!")

    # Assert
    assert msg.get_body() == b"Hello, Service Bus!"


def test_message_with_bytes_body() -> None:
    """Test Service Bus message with binary data."""
    # Arrange
    binary_data = b"\x00\x01\x02\x03"
    msg = mock_service_bus_message(binary_data)

    # Assert
    assert msg.get_body() == binary_data


# =============================================================================
# EXAMPLE: Partition Key
# =============================================================================
def test_message_with_partition_key() -> None:
    """Test Service Bus message with partition key."""
    # Arrange
    msg = mock_service_bus_message(
        {"order_id": 123},
        partition_key="customer-456",
        session_id="session-456",
    )

    # Assert
    assert msg.partition_key == "customer-456"
    assert msg.session_id == "session-456"


if __name__ == "__main__":
    # Run all test examples
    test_process_order_message()
    test_process_session_message()
    test_process_with_max_retries_exceeded()
    test_process_within_retry_limit()
    test_process_high_priority_message()
    test_process_dead_letter_message()
    test_process_correlated_message()
    test_message_with_user_properties()
    test_message_with_timing_metadata()
    test_message_with_string_body()
    test_message_with_bytes_body()
    test_message_with_partition_key()
    print("✓ All Service Bus message examples passed!")
