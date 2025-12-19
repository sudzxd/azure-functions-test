"""Unit tests for ServiceBusMessage mock."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from datetime import UTC, datetime

# Project/Local
from azure_functions_test import mock_service_bus_message


# =============================================================================
# TESTS: Initialization & Defaults
# =============================================================================
def test_mock_service_bus_message_uses_defaults_when_no_args() -> None:
    """mock_service_bus_message() should use default values when called with no args."""
    msg = mock_service_bus_message()

    assert msg.message_id == "test-message-id"
    assert msg.get_body() == b""
    assert msg.session_id is None
    assert msg.partition_key is None
    assert msg.delivery_count == 1
    assert msg.enqueued_time_utc is not None
    assert msg.application_properties == {}
    assert msg.user_properties == {}


def test_mock_service_bus_message_uses_empty_body_by_default() -> None:
    """mock_service_bus_message() should use empty bytes body by default."""
    msg = mock_service_bus_message()

    assert msg.get_body() == b""


# =============================================================================
# TESTS: Body Serialization - Dict
# =============================================================================
def test_mock_service_bus_message_dict_body_serialized_to_json() -> None:
    """Dict body should be JSON-serialized to bytes."""
    msg = mock_service_bus_message({"order_id": 123, "status": "pending"})

    body = msg.get_body()
    assert isinstance(body, bytes)
    assert body == b'{"order_id": 123, "status": "pending"}'


def test_mock_service_bus_message_nested_dict_body() -> None:
    """Nested dict should be serialized correctly."""
    msg = mock_service_bus_message({"user": {"name": "Alice", "age": 30}})

    body = msg.get_body()
    assert b'"user"' in body
    assert b'"name"' in body
    assert b'"Alice"' in body


# =============================================================================
# TESTS: Body Serialization - String
# =============================================================================
def test_mock_service_bus_message_string_body_encoded_to_utf8() -> None:
    """String body should be UTF-8 encoded to bytes."""
    msg = mock_service_bus_message("Hello, Service Bus!")

    body = msg.get_body()
    assert isinstance(body, bytes)
    assert body == b"Hello, Service Bus!"


def test_mock_service_bus_message_string_body_with_unicode() -> None:
    """String with Unicode characters should be encoded correctly."""
    msg = mock_service_bus_message("Hello, 世界! 🌍")

    body = msg.get_body()
    assert body.decode("utf-8") == "Hello, 世界! 🌍"


# =============================================================================
# TESTS: Body Serialization - Bytes
# =============================================================================
def test_mock_service_bus_message_bytes_body_used_as_is() -> None:
    """Bytes body should be used as-is without modification."""
    msg = mock_service_bus_message(b"\x00\x01\x02\x03")

    body = msg.get_body()
    assert body == b"\x00\x01\x02\x03"


# =============================================================================
# TESTS: Body Serialization - None
# =============================================================================
def test_mock_service_bus_message_none_body_becomes_empty_bytes() -> None:
    """None body should become empty bytes."""
    msg = mock_service_bus_message(None)

    assert msg.get_body() == b""


# =============================================================================
# TESTS: Basic Metadata
# =============================================================================
def test_mock_service_bus_message_custom_message_id() -> None:
    """Custom message_id should override the default."""
    msg = mock_service_bus_message("test", message_id="custom-msg-123")

    assert msg.message_id == "custom-msg-123"


def test_mock_service_bus_message_custom_content_type() -> None:
    """Custom content_type should be set correctly."""
    msg = mock_service_bus_message("test", content_type="application/json")

    assert msg.content_type == "application/json"


def test_mock_service_bus_message_custom_correlation_id() -> None:
    """Custom correlation_id should be set correctly."""
    msg = mock_service_bus_message("test", correlation_id="corr-456")

    assert msg.correlation_id == "corr-456"


# =============================================================================
# TESTS: Session Support
# =============================================================================
def test_mock_service_bus_message_session_id() -> None:
    """Session ID should be set correctly."""
    msg = mock_service_bus_message("test", session_id="session-1")

    assert msg.session_id == "session-1"


def test_mock_service_bus_message_partition_key() -> None:
    """Partition key should be set correctly."""
    msg = mock_service_bus_message("test", partition_key="partition-1")

    assert msg.partition_key == "partition-1"


def test_mock_service_bus_message_session_and_partition() -> None:
    """Session ID and partition key should work together."""
    msg = mock_service_bus_message(
        "test", session_id="session-1", partition_key="partition-1"
    )

    assert msg.session_id == "session-1"
    assert msg.partition_key == "partition-1"


# =============================================================================
# TESTS: Delivery Tracking
# =============================================================================
def test_mock_service_bus_message_default_delivery_count() -> None:
    """Default delivery_count should be 1."""
    msg = mock_service_bus_message("test")

    assert msg.delivery_count == 1


def test_mock_service_bus_message_custom_delivery_count() -> None:
    """Custom delivery_count should override the default."""
    msg = mock_service_bus_message("test", delivery_count=5)

    assert msg.delivery_count == 5


def test_mock_service_bus_message_zero_delivery_count() -> None:
    """Delivery count of 0 should be valid."""
    msg = mock_service_bus_message("test", delivery_count=0)

    assert msg.delivery_count == 0


# =============================================================================
# TESTS: Timing Metadata
# =============================================================================
def test_mock_service_bus_message_default_enqueued_time() -> None:
    """Default enqueued_time_utc should be current UTC time."""
    msg = mock_service_bus_message("test")

    assert msg.enqueued_time_utc is not None
    assert isinstance(msg.enqueued_time_utc, datetime)
    assert msg.enqueued_time_utc.tzinfo == UTC


def test_mock_service_bus_message_custom_enqueued_time() -> None:
    """Custom enqueued_time_utc should override the default."""
    custom_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    msg = mock_service_bus_message("test", enqueued_time_utc=custom_time)

    assert msg.enqueued_time_utc == custom_time


def test_mock_service_bus_message_expires_at() -> None:
    """Expires_at_utc should be set correctly."""
    expiry = datetime(2025, 12, 31, 23, 59, 59, tzinfo=UTC)
    msg = mock_service_bus_message("test", expires_at_utc=expiry)

    assert msg.expires_at_utc == expiry


# =============================================================================
# TESTS: Dead Letter Support
# =============================================================================
def test_mock_service_bus_message_dead_letter_source() -> None:
    """Dead letter source should be set correctly."""
    msg = mock_service_bus_message("test", dead_letter_source="original-queue")

    assert msg.dead_letter_source == "original-queue"


def test_mock_service_bus_message_dead_letter_reason() -> None:
    """Dead letter reason should be set correctly."""
    msg = mock_service_bus_message("test", dead_letter_reason="ProcessingError")

    assert msg.dead_letter_reason == "ProcessingError"


def test_mock_service_bus_message_dead_letter_description() -> None:
    """Dead letter error description should be set correctly."""
    msg = mock_service_bus_message(
        "test",
        dead_letter_error_description="Message processing failed after 5 retries",
    )

    assert (
        msg.dead_letter_error_description == "Message processing failed after 5 retries"
    )


def test_mock_service_bus_message_dead_letter_all_fields() -> None:
    """All dead letter fields should work together."""
    msg = mock_service_bus_message(
        "failed message",
        dead_letter_source="orders-queue",
        dead_letter_reason="ValidationError",
        dead_letter_error_description="Invalid order data",
    )

    assert msg.dead_letter_source == "orders-queue"
    assert msg.dead_letter_reason == "ValidationError"
    assert msg.dead_letter_error_description == "Invalid order data"


# =============================================================================
# TESTS: Application Properties
# =============================================================================
def test_mock_service_bus_message_empty_application_properties() -> None:
    """Empty application_properties should work correctly."""
    msg = mock_service_bus_message("test", application_properties={})

    assert msg.application_properties == {}


def test_mock_service_bus_message_application_properties() -> None:
    """Application properties should be set correctly."""
    props = {"priority": "high", "version": "1.0", "retry_count": 3}
    msg = mock_service_bus_message("test", application_properties=props)

    assert msg.application_properties["priority"] == "high"
    assert msg.application_properties["version"] == "1.0"
    assert msg.application_properties["retry_count"] == 3


# =============================================================================
# TESTS: User Properties
# =============================================================================
def test_mock_service_bus_message_empty_user_properties() -> None:
    """Empty user_properties should work correctly."""
    msg = mock_service_bus_message("test", user_properties={})

    assert msg.user_properties == {}


def test_mock_service_bus_message_user_properties() -> None:
    """User properties should be set correctly."""
    props = {"source": "api", "user_id": 123, "tenant": "tenant-abc"}
    msg = mock_service_bus_message("test", user_properties=props)

    assert msg.user_properties["source"] == "api"
    assert msg.user_properties["user_id"] == 123
    assert msg.user_properties["tenant"] == "tenant-abc"


def test_mock_service_bus_message_application_and_user_properties() -> None:
    """Application and user properties should work together."""
    app_props = {"priority": "high"}
    user_props = {"source": "api"}
    msg = mock_service_bus_message(
        "test", application_properties=app_props, user_properties=user_props
    )

    assert msg.application_properties["priority"] == "high"
    assert msg.user_properties["source"] == "api"


# =============================================================================
# TESTS: Edge Cases
# =============================================================================
def test_mock_service_bus_message_empty_dict_body() -> None:
    """Empty dict should serialize correctly."""
    msg = mock_service_bus_message({})

    assert msg.get_body() == b"{}"


def test_mock_service_bus_message_empty_string_body() -> None:
    """Empty string should encode to empty bytes."""
    msg = mock_service_bus_message("")

    assert msg.get_body() == b""


# =============================================================================
# TESTS: Multiple Instances
# =============================================================================
def test_mock_service_bus_message_multiple_instances_independent() -> None:
    """Multiple message instances should be independent."""
    msg1 = mock_service_bus_message(
        {"order": 1}, message_id="msg-1", session_id="session-1"
    )
    msg2 = mock_service_bus_message(
        {"order": 2}, message_id="msg-2", session_id="session-2"
    )

    assert msg1.get_body() == b'{"order": 1}'
    assert msg2.get_body() == b'{"order": 2}'
    assert msg1.message_id == "msg-1"
    assert msg2.message_id == "msg-2"
    assert msg1.session_id == "session-1"
    assert msg2.session_id == "session-2"


# =============================================================================
# TESTS: Integration with Real Use Cases
# =============================================================================
def test_mock_service_bus_message_order_processing() -> None:
    """Should support testing order processing scenarios."""
    msg = mock_service_bus_message(
        {"order_id": "ORD-123", "items": ["item1", "item2"], "total": 99.99},
        message_id="order-msg-123",
        session_id="customer-456",
        application_properties={"priority": "high", "region": "us-west"},
    )

    assert msg.message_id == "order-msg-123"
    assert msg.session_id == "customer-456"
    assert msg.application_properties["priority"] == "high"
    assert b"ORD-123" in msg.get_body()


def test_mock_service_bus_message_retry_logic() -> None:
    """Should support testing retry logic based on delivery count."""
    msg = mock_service_bus_message({"data": "test"}, delivery_count=5)

    # Simulate retry logic
    max_retries = 5
    should_retry = msg.delivery_count <= max_retries  # type: ignore[operator]

    assert should_retry is True


def test_mock_service_bus_message_dead_letter_processing() -> None:
    """Should support testing dead letter queue processing."""
    msg = mock_service_bus_message(
        "failed message",
        dead_letter_source="main-queue",
        dead_letter_reason="MessageExpired",
        dead_letter_error_description="Message TTL exceeded",
        delivery_count=10,
    )

    assert msg.dead_letter_source == "main-queue"
    assert msg.dead_letter_reason == "MessageExpired"
    assert msg.delivery_count == 10


def test_mock_service_bus_message_with_all_parameters() -> None:
    """All parameters should work together."""
    enqueued_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    expires_at = datetime(2025, 1, 2, 12, 0, 0, tzinfo=UTC)

    msg = mock_service_bus_message(
        {"order_id": 456, "status": "processing"},
        message_id="msg-456",
        session_id="session-abc",
        partition_key="partition-1",
        content_type="application/json",
        correlation_id="corr-789",
        delivery_count=3,
        enqueued_time_utc=enqueued_time,
        expires_at_utc=expires_at,
        dead_letter_source="original-queue",
        dead_letter_reason="ProcessingError",
        dead_letter_error_description="Failed to process",
        application_properties={"priority": "high"},
        user_properties={"source": "api"},
    )

    assert msg.get_body() == b'{"order_id": 456, "status": "processing"}'
    assert msg.message_id == "msg-456"
    assert msg.session_id == "session-abc"
    assert msg.partition_key == "partition-1"
    assert msg.content_type == "application/json"
    assert msg.correlation_id == "corr-789"
    assert msg.delivery_count == 3
    assert msg.enqueued_time_utc == enqueued_time
    assert msg.expires_at_utc == expires_at
    assert msg.dead_letter_source == "original-queue"
    assert msg.dead_letter_reason == "ProcessingError"
    assert msg.dead_letter_error_description == "Failed to process"
    assert msg.application_properties["priority"] == "high"
    assert msg.user_properties["source"] == "api"
