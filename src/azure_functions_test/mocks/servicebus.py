"""Service Bus message mock implementation.

This module provides a duck-typed mock for Azure Service Bus messages
with Pydantic validation and full type safety.
"""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import json
from datetime import UTC, datetime, timedelta
from typing import Any

# Third-party
from pydantic import Field
from pydantic.dataclasses import dataclass

# Project/Local
from .._internal import get_logger
from ..protocols import ServiceBusMessageProtocol

# =============================================================================
# LOGGER
# =============================================================================
logger = get_logger(__name__)


# =============================================================================
# CORE CLASSES
# =============================================================================
@dataclass
class ServiceBusMessageMock:
    """Duck-typed mock for Azure Service Bus messages.

    This class implements the ServiceBusMessageProtocol interface using Pydantic
    dataclass for validation and type safety. It provides comprehensive support
    for all Service Bus message properties.

    Attributes:
        message_id: Unique message identifier. Defaults to "test-message-id".
        body: Message body as bytes. Defaults to empty bytes.
        session_id: Session identifier for session-aware entities. Defaults to None.
        partition_key: Partition key for partitioned entities. Defaults to None.
        content_type: Content type descriptor. Defaults to None.
        correlation_id: Correlation identifier. Defaults to None.
        delivery_count: Number of times delivered. Defaults to 1.
        enqueued_time_utc: UTC time when enqueued. Defaults to current time.
        expires_at_utc: UTC time when expires. Defaults to None.
        expiration_time: UTC time when expires (legacy). Defaults to None.
        dead_letter_source: Source queue/subscription if dead. Defaults to None.
        dead_letter_reason: Reason for dead lettering. Defaults to None.
        dead_letter_error_description: Error description. Defaults to None.
        locked_until: UTC time until locked. Defaults to None.
        lock_token: Lock token for operations. Defaults to None.
        sequence_number: Unique sequence number. Defaults to None.
        enqueued_sequence_number: Original sequence number. Defaults to None.
        scheduled_enqueue_time: Scheduled time. Defaults to None.
        scheduled_enqueue_time_utc: Scheduled time (explicit UTC). Defaults to None.
        label: Application-specific label. Defaults to None.
        subject: Message subject. Defaults to None.
        reply_to: Reply address. Defaults to None.
        reply_to_session_id: Reply session ID. Defaults to None.
        to: Destination address. Defaults to None.
        time_to_live: Time to live duration. Defaults to None.
        state: Message state. Defaults to None.
        transaction_partition_key: Transaction partition key. Defaults to None.
        application_properties: Application properties. Defaults to empty dict.
        user_properties: User properties. Defaults to empty dict.
        metadata: Message metadata. Defaults to None.

    Examples:
        Create a simple message:

        >>> msg = ServiceBusMessageMock(
        ...     message_id="msg-123",
        ...     body=b"Hello, Service Bus!"
        ... )
        >>> msg.message_id
        'msg-123'

        Create a session-aware message:

        >>> msg = ServiceBusMessageMock(
        ...     message_id="msg-456",
        ...     session_id="session-1",
        ...     body=b"Session message"
        ... )
        >>> msg.session_id
        'session-1'
    """

    message_id: str = Field(default="test-message-id")
    body: bytes = Field(default=b"")
    session_id: str | None = Field(default=None)
    partition_key: str | None = Field(default=None)
    content_type: str | None = Field(default=None)
    correlation_id: str | None = Field(default=None)
    delivery_count: int | None = Field(default=1)
    enqueued_time_utc: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    expires_at_utc: datetime | None = Field(default=None)
    expiration_time: datetime | None = Field(default=None)
    dead_letter_source: str | None = Field(default=None)
    dead_letter_reason: str | None = Field(default=None)
    dead_letter_error_description: str | None = Field(default=None)
    locked_until: datetime | None = Field(default=None)
    lock_token: str | None = Field(default=None)
    sequence_number: int | None = Field(default=None)
    enqueued_sequence_number: int | None = Field(default=None)
    scheduled_enqueue_time: datetime | None = Field(default=None)
    scheduled_enqueue_time_utc: datetime | None = Field(default=None)
    label: str | None = Field(default=None)
    subject: str | None = Field(default=None)
    reply_to: str | None = Field(default=None)
    reply_to_session_id: str | None = Field(default=None)
    to: str | None = Field(default=None)
    time_to_live: timedelta | None = Field(default=None)
    state: int | None = Field(default=None)
    transaction_partition_key: str | None = Field(default=None)
    application_properties: dict[str, Any] = Field(default_factory=dict)
    user_properties: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] | None = Field(default=None)

    def get_body(self) -> bytes:
        """Return message body as bytes.

        Returns:
            Message body as bytes.

        Examples:
            >>> msg = ServiceBusMessageMock(body=b"test")
            >>> msg.get_body()
            b'test'
        """
        return self.body

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation showing message ID and memory address.

        Examples:
            >>> msg = ServiceBusMessageMock(message_id="msg-123")
            >>> repr(msg)
            "<ServiceBusMessageMock message_id='msg-123' at 0x...>"
        """
        return (
            f"<ServiceBusMessageMock message_id={self.message_id!r} at {hex(id(self))}>"
        )

    @staticmethod
    def serialize_body(
        body: dict[Any, Any] | str | bytes | None,
    ) -> bytes:
        """Serialize message body to bytes.

        Args:
            body: Message body to serialize. Accepts:
                - dict: JSON-serialized to UTF-8 bytes
                - str: UTF-8 encoded to bytes
                - bytes: Returned as-is
                - None: Returns empty bytes

        Returns:
            Serialized body as bytes.

        Examples:
            >>> ServiceBusMessageMock.serialize_body({"key": "value"})
            b'{"key": "value"}'
            >>> ServiceBusMessageMock.serialize_body("Hello")
            b'Hello'
            >>> ServiceBusMessageMock.serialize_body(None)
            b''
        """
        if body is None:
            return b""
        if isinstance(body, bytes):
            return body
        if isinstance(body, str):
            return body.encode("utf-8")
        # Must be dict (only remaining valid type)
        return json.dumps(body).encode("utf-8")


# =============================================================================
# PUBLIC API
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
    dead_letter_source: str | None = None,
    dead_letter_reason: str | None = None,
    dead_letter_error_description: str | None = None,
    application_properties: dict[str, Any] | None = None,
    user_properties: dict[str, Any] | None = None,
) -> ServiceBusMessageProtocol:
    """Create a mock ServiceBusMessage for testing.

    Provides a test double for Azure Service Bus trigger inputs with
    automatic body serialization and sensible defaults. Returns an object
    that implements ServiceBusMessageProtocol.

    Args:
        body: Message body. Dicts are JSON-serialized automatically.
            Strings are UTF-8 encoded. Bytes are used as-is.
        message_id: Unique message identifier. Defaults to "test-message-id".
        session_id: Session identifier. Defaults to None.
        partition_key: Partition key. Defaults to None.
        content_type: Content type descriptor. Defaults to None.
        correlation_id: Correlation identifier. Defaults to None.
        delivery_count: Number of times delivered. Defaults to 1.
        enqueued_time_utc: UTC time when enqueued. Defaults to current time.
        expires_at_utc: UTC time when expires. Defaults to None.
        dead_letter_source: Source if dead lettered. Defaults to None.
        dead_letter_reason: Dead letter reason. Defaults to None.
        dead_letter_error_description: Dead letter error description. Defaults to None.
        application_properties: Application properties. Defaults to empty dict.
        user_properties: User properties. Defaults to empty dict.

    Returns:
        A ServiceBusMessageMock instance implementing ServiceBusMessageProtocol.

    Examples:
        Create a simple message:

        >>> msg = mock_service_bus_message("Hello, Service Bus!")
        >>> msg.get_body().decode()
        'Hello, Service Bus!'

        Create a message with JSON body:

        >>> msg = mock_service_bus_message(
        ...     {"order_id": 123, "status": "pending"},
        ...     message_id="order-123"
        ... )
        >>> msg.message_id
        'order-123'

        Create a session-aware message:

        >>> msg = mock_service_bus_message(
        ...     "Session message",
        ...     session_id="session-1",
        ...     partition_key="partition-1"
        ... )
        >>> msg.session_id
        'session-1'

        Create a dead-lettered message:

        >>> msg = mock_service_bus_message(
        ...     "Failed message",
        ...     dead_letter_source="original-queue",
        ...     dead_letter_reason="ProcessingError",
        ...     dead_letter_error_description="Message processing fail after 5 retries"
        ... )
        >>> msg.dead_letter_reason
        'ProcessingError'
    """
    logger.debug(
        "Creating ServiceBusMessageMock with message_id=%s",
        message_id or "test-message-id",
    )

    # Serialize body if provided
    serialized_body = ServiceBusMessageMock.serialize_body(body)

    # Build kwargs
    kwargs: dict[str, Any] = {"body": serialized_body}
    if message_id is not None:
        kwargs["message_id"] = message_id
    if session_id is not None:
        kwargs["session_id"] = session_id
    if partition_key is not None:
        kwargs["partition_key"] = partition_key
    if content_type is not None:
        kwargs["content_type"] = content_type
    if correlation_id is not None:
        kwargs["correlation_id"] = correlation_id
    if delivery_count is not None:
        kwargs["delivery_count"] = delivery_count
    if enqueued_time_utc is not None:
        kwargs["enqueued_time_utc"] = enqueued_time_utc
    if expires_at_utc is not None:
        kwargs["expires_at_utc"] = expires_at_utc
    if dead_letter_source is not None:
        kwargs["dead_letter_source"] = dead_letter_source
    if dead_letter_reason is not None:
        kwargs["dead_letter_reason"] = dead_letter_reason
    if dead_letter_error_description is not None:
        kwargs["dead_letter_error_description"] = dead_letter_error_description
    if application_properties is not None:
        kwargs["application_properties"] = application_properties
    if user_properties is not None:
        kwargs["user_properties"] = user_properties

    return ServiceBusMessageMock(**kwargs)
