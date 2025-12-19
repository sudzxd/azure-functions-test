"""Unit tests for QueueMessage mock."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from datetime import UTC, datetime

# Project/Local
from azure_functions_test import mock_queue_message


# =============================================================================
# TESTS: Initialization & Defaults
# =============================================================================
def test_mock_queue_message_uses_defaults_when_no_args() -> None:
    """mock_queue_message() should use default values when called with no args."""
    msg = mock_queue_message()

    assert msg.id == "test-message-id"
    assert msg.dequeue_count == 1
    assert msg.pop_receipt == "test-pop-receipt"
    assert msg.expiration_time is None
    assert msg.time_next_visible is None
    assert msg.insertion_time is not None  # Should have a default timestamp


def test_mock_queue_message_uses_empty_body_by_default() -> None:
    """mock_queue_message() should use empty bytes body by default."""
    msg = mock_queue_message()

    assert msg.get_body() == b""


# =============================================================================
# TESTS: Body Serialization - Dict
# =============================================================================
def test_mock_queue_message_dict_body_serialized_to_json() -> None:
    """Dict body should be JSON-serialized to bytes."""
    msg = mock_queue_message({"order_id": 123, "status": "pending"})

    body = msg.get_body()
    assert isinstance(body, bytes)
    assert body == b'{"order_id": 123, "status": "pending"}'


def test_mock_queue_message_dict_body_get_json_returns_dict() -> None:
    """get_json() should return the original dict."""
    msg = mock_queue_message({"order_id": 123, "status": "pending"})

    data = msg.get_json()
    assert data == {"order_id": 123, "status": "pending"}


def test_mock_queue_message_nested_dict_body() -> None:
    """Nested dict should be serialized correctly."""
    msg = mock_queue_message({"user": {"name": "Alice", "age": 30}})

    data = msg.get_json()
    assert data == {"user": {"name": "Alice", "age": 30}}


# =============================================================================
# TESTS: Body Serialization - List
# =============================================================================
def test_mock_queue_message_list_body_serialized_to_json() -> None:
    """List body should be JSON-serialized to bytes."""
    msg = mock_queue_message([1, 2, 3, 4, 5])

    body = msg.get_body()
    assert isinstance(body, bytes)
    assert body == b"[1, 2, 3, 4, 5]"


def test_mock_queue_message_list_body_get_json_returns_list() -> None:
    """get_json() should return the original list."""
    msg = mock_queue_message([1, 2, 3, 4, 5])

    data = msg.get_json()
    assert data == [1, 2, 3, 4, 5]


# =============================================================================
# TESTS: Body Serialization - String
# =============================================================================
def test_mock_queue_message_string_body_encoded_to_utf8() -> None:
    """String body should be UTF-8 encoded to bytes."""
    msg = mock_queue_message("Hello, World!")

    body = msg.get_body()
    assert isinstance(body, bytes)
    assert body == b"Hello, World!"


def test_mock_queue_message_string_body_with_unicode() -> None:
    """String with Unicode characters should be encoded correctly."""
    msg = mock_queue_message("Hello, 世界! 🌍")

    body = msg.get_body()
    assert body.decode("utf-8") == "Hello, 世界! 🌍"


# =============================================================================
# TESTS: Body Serialization - Bytes
# =============================================================================
def test_mock_queue_message_bytes_body_used_as_is() -> None:
    """Bytes body should be used as-is without modification."""
    msg = mock_queue_message(b"\x00\x01\x02\x03")

    body = msg.get_body()
    assert body == b"\x00\x01\x02\x03"


# =============================================================================
# TESTS: Body Serialization - None
# =============================================================================
def test_mock_queue_message_none_body_becomes_empty_bytes() -> None:
    """None body should become empty bytes."""
    msg = mock_queue_message(None)

    body = msg.get_body()
    assert body == b""


# =============================================================================
# TESTS: Custom Metadata
# =============================================================================
def test_mock_queue_message_custom_id() -> None:
    """Custom ID should override the default."""
    msg = mock_queue_message({"data": "test"}, id="custom-message-id")

    assert msg.id == "custom-message-id"


def test_mock_queue_message_custom_dequeue_count() -> None:
    """Custom dequeue_count should override the default."""
    msg = mock_queue_message({"data": "test"}, dequeue_count=5)

    assert msg.dequeue_count == 5


def test_mock_queue_message_custom_pop_receipt() -> None:
    """Custom pop_receipt should override the default."""
    msg = mock_queue_message({"data": "test"}, pop_receipt="custom-receipt")

    assert msg.pop_receipt == "custom-receipt"


def test_mock_queue_message_custom_expiration_time() -> None:
    """Custom expiration_time should be stored."""
    expiration = datetime(2025, 12, 31, 23, 59, 59, tzinfo=UTC)
    msg = mock_queue_message({"data": "test"}, expiration_time=expiration)

    assert msg.expiration_time == expiration


def test_mock_queue_message_custom_insertion_time() -> None:
    """Custom insertion_time should override the default."""
    insertion = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    msg = mock_queue_message({"data": "test"}, insertion_time=insertion)

    assert msg.insertion_time == insertion


def test_mock_queue_message_custom_time_next_visible() -> None:
    """Custom time_next_visible should be stored."""
    next_visible = datetime(2025, 1, 2, 12, 0, 0, tzinfo=UTC)
    msg = mock_queue_message({"data": "test"}, time_next_visible=next_visible)

    assert msg.time_next_visible == next_visible


# =============================================================================
# TESTS: Edge Cases
# =============================================================================
def test_mock_queue_message_empty_dict_body() -> None:
    """Empty dict should serialize correctly."""
    msg = mock_queue_message({})

    assert msg.get_json() == {}
    assert msg.get_body() == b"{}"


def test_mock_queue_message_empty_list_body() -> None:
    """Empty list should serialize correctly."""
    msg = mock_queue_message([])

    assert msg.get_json() == []
    assert msg.get_body() == b"[]"


def test_mock_queue_message_empty_string_body() -> None:
    """Empty string should encode to empty bytes."""
    msg = mock_queue_message("")

    assert msg.get_body() == b""


def test_mock_queue_message_zero_dequeue_count() -> None:
    """Dequeue count of 0 should be valid."""
    msg = mock_queue_message({"data": "test"}, dequeue_count=0)

    assert msg.dequeue_count == 0


# =============================================================================
# TESTS: Multiple Instances
# =============================================================================
def test_mock_queue_message_multiple_instances_independent() -> None:
    """Multiple message instances should be independent."""
    msg1 = mock_queue_message({"order": 1}, id="msg-1")
    msg2 = mock_queue_message({"order": 2}, id="msg-2")

    assert msg1.get_json() == {"order": 1}
    assert msg2.get_json() == {"order": 2}
    assert msg1.id == "msg-1"
    assert msg2.id == "msg-2"


# =============================================================================
# TESTS: Integration with Real Use Cases
# =============================================================================
def test_mock_queue_message_poison_message_simulation() -> None:
    """Should support testing poison message handling (high dequeue_count)."""
    msg = mock_queue_message({"order_id": 123}, dequeue_count=6)

    # Simulate poison message detection logic
    assert msg.dequeue_count is not None
    is_poison = msg.dequeue_count > 5

    assert is_poison is True


def test_mock_queue_message_with_all_parameters() -> None:
    """All parameters should work together."""
    expiration = datetime(2025, 12, 31, 23, 59, 59, tzinfo=UTC)
    insertion = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    next_visible = datetime(2025, 1, 2, 12, 0, 0, tzinfo=UTC)

    msg = mock_queue_message(
        {"order_id": 456, "status": "processing"},
        id="msg-456",
        dequeue_count=3,
        expiration_time=expiration,
        insertion_time=insertion,
        time_next_visible=next_visible,
        pop_receipt="receipt-xyz",
    )

    assert msg.get_json() == {"order_id": 456, "status": "processing"}
    assert msg.id == "msg-456"
    assert msg.dequeue_count == 3
    assert msg.expiration_time == expiration
    assert msg.insertion_time == insertion
    assert msg.time_next_visible == next_visible
    assert msg.pop_receipt == "receipt-xyz"
