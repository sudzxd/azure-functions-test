"""Example: Testing Azure Queue Storage triggered functions."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import json
from typing import Any

# Third-party
from azure.functions import Out

# Project/Local
from azure_functions_test import FunctionTestContext, mock_queue_message
from azure_functions_test.protocols import QueueMessageProtocol


# =============================================================================
# EXAMPLE: Simple Queue Message Processing
# =============================================================================
def process_order_queue(msg: QueueMessageProtocol, output: Out[str]) -> None:
    """Process order from queue and write to output binding.

    Args:
        msg: Queue message containing order data.
        output: Output binding for processed results.
    """
    order_data = msg.get_json()
    order_id = order_data.get("order_id")

    # Simulate order processing
    result = {
        "order_id": order_id,
        "status": "processed",
        "message_id": msg.id,
    }

    # Write to output binding
    output.set(json.dumps(result))


def test_process_order_queue() -> None:
    """Test basic queue message processing."""
    # Arrange
    order_data = {"order_id": 123, "items": ["item1", "item2"], "total": 99.99}
    msg = mock_queue_message(order_data)
    ctx = FunctionTestContext()

    # Act
    process_order_queue(msg, ctx.out("processedOrder"))

    # Assert
    output = json.loads(ctx.outputs["processedOrder"])
    assert output["order_id"] == 123
    assert output["status"] == "processed"
    assert output["message_id"] == "test-message-id"


# =============================================================================
# EXAMPLE: Poison Message Detection
# =============================================================================
def process_with_retry(
    msg: QueueMessageProtocol, poison_out: Out[str], data_out: Out[str]
) -> None:
    """Process message with poison message detection.

    Args:
        msg: Queue message with dequeue count tracking.
        poison_out: Output binding for poison messages.
        data_out: Output binding for processed data.
    """
    max_retries = 5

    if msg.dequeue_count is not None and msg.dequeue_count > max_retries:
        # Move to poison queue
        poison_out.set(
            json.dumps(
                {
                    "message_id": msg.id,
                    "reason": "Max retries exceeded",
                    "dequeue_count": msg.dequeue_count,
                }
            )
        )
        return

    # Normal processing
    data = msg.get_json()
    data_out.set(json.dumps(data))


def test_poison_message_detection() -> None:
    """Test that poison messages are detected and moved to poison queue."""
    # Arrange
    msg = mock_queue_message({"data": "test"}, dequeue_count=6)
    ctx = FunctionTestContext()

    # Act
    process_with_retry(msg, ctx.out("poisonQueue"), ctx.out("processedData"))

    # Assert
    poison_output = json.loads(ctx.outputs["poisonQueue"])
    assert poison_output["reason"] == "Max retries exceeded"
    assert poison_output["dequeue_count"] == 6


# =============================================================================
# EXAMPLE: Different Body Types
# =============================================================================
def test_queue_message_with_string_body() -> None:
    """Test processing queue message with string body."""
    # Arrange
    msg = mock_queue_message("Hello, Queue!")

    # Act
    body = msg.get_body()

    # Assert
    assert body == b"Hello, Queue!"
    assert body.decode("utf-8") == "Hello, Queue!"


def test_queue_message_with_bytes_body() -> None:
    """Test processing queue message with binary data."""
    # Arrange
    binary_data = b"\x00\x01\x02\x03"
    msg = mock_queue_message(binary_data)

    # Act
    body = msg.get_body()

    # Assert
    assert body == binary_data


def test_queue_message_with_list_body() -> None:
    """Test processing queue message with list (JSON array)."""
    # Arrange
    items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    msg = mock_queue_message(items)

    # Act
    data: list[dict[str, Any]] = msg.get_json()

    # Assert
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["id"] == 1


# =============================================================================
# EXAMPLE: Custom Message Properties
# =============================================================================
def test_queue_message_with_custom_properties() -> None:
    """Test queue message with custom metadata."""
    # Arrange
    msg = mock_queue_message(
        {"order_id": 456},
        id="custom-msg-123",
        dequeue_count=3,
        pop_receipt="receipt-xyz",
    )

    # Assert
    assert msg.id == "custom-msg-123"
    assert msg.dequeue_count == 3
    assert msg.pop_receipt == "receipt-xyz"


if __name__ == "__main__":
    # Run all test examples
    test_process_order_queue()
    test_poison_message_detection()
    test_queue_message_with_string_body()
    test_queue_message_with_bytes_body()
    test_queue_message_with_list_body()
    test_queue_message_with_custom_properties()
    print("✓ All queue message examples passed!")
