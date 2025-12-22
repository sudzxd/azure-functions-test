"""Service Bus message mock implementation.

This module provides a duck-typed mock for Azure Service Bus messages
with Pydantic validation and full type safety.
"""

from __future__ import annotations

import uuid

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from datetime import UTC, datetime, timedelta
from typing import Any

# Third-party
from pydantic import Field
from pydantic.dataclasses import dataclass

# Project/Local
from .._internal import get_logger, serialize_to_bytes
from ..protocols import ServiceBusMessageProtocol
from .base import filter_none

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
    delivery_count: int = Field(default=1)
    enqueued_time_utc: datetime = Field(default_factory=lambda: datetime.now(UTC))
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
) -> ServiceBusMessageProtocol:
    """Create a mock ServiceBusMessage for testing.

    Provides a test double for Azure Service Bus trigger inputs with
    automatic body serialization and sensible defaults. Returns an object
    that implements ServiceBusMessageProtocol.

    Args:
        body: Message body. Dicts are JSON-serialized automatically.
            Strings are UTF-8 encoded. Bytes are used as-is.
        message_id: Unique message identifier. Defaults to "test-message-id".
        session_id: Session identifier for session-aware entities. Defaults to None.
        partition_key: Partition key for partitioned entities. Defaults to None.
        content_type: Content type descriptor. Defaults to None.
        correlation_id: Correlation identifier for request-reply patterns.
            Defaults to None.
        delivery_count: Number of times delivered. Defaults to 1.
        enqueued_time_utc: UTC time when enqueued. Defaults to current time.
        expires_at_utc: UTC time when message expires. Defaults to None.
        expiration_time: UTC time when message expires (legacy property).
            Defaults to None.
        dead_letter_source: Source queue/subscription if dead lettered.
            Defaults to None.
        dead_letter_reason: Reason for dead lettering. Defaults to None.
        dead_letter_error_description: Error description for dead lettering.
            Defaults to None.
        locked_until: UTC time until message is locked in queue. Defaults to None.
        lock_token: Lock token for message operations (peek-lock). Defaults to None.
        sequence_number: Unique sequence number assigned by Service Bus.
            Defaults to None.
        enqueued_sequence_number: Original sequence number when auto-forwarded.
            Defaults to None.
        scheduled_enqueue_time: UTC time for scheduled message availability.
            Defaults to None.
        scheduled_enqueue_time_utc: UTC time for scheduled message (explicit UTC).
            Defaults to None.
        label: Application-specific label for routing. Defaults to None.
        subject: Message subject for routing. Defaults to None.
        reply_to: Address of queue/topic to reply to. Defaults to None.
        reply_to_session_id: Session identifier to reply to. Defaults to None.
        to: Destination address for routing. Defaults to None.
        time_to_live: Message time to live duration. Defaults to None.
        state: Message state for tracking. Defaults to None.
        transaction_partition_key: Partition key for transactional operations.
            Defaults to None.
        application_properties: Application-specific properties. Defaults to empty dict.
        user_properties: User-defined properties. Defaults to empty dict.
        metadata: Message metadata. Defaults to None.

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

        Create a message with sequence ordering:

        >>> msg = mock_service_bus_message(
        ...     {"order": "data"},
        ...     sequence_number=12345,
        ...     enqueued_sequence_number=12300
        ... )
        >>> msg.sequence_number
        12345

        Create a scheduled message:

        >>> from datetime import datetime, UTC, timedelta
        >>> scheduled_time = datetime.now(UTC) + timedelta(hours=1)
        >>> msg = mock_service_bus_message(
        ...     "Scheduled message",
        ...     scheduled_enqueue_time_utc=scheduled_time
        ... )

        Create a request-reply message:

        >>> msg = mock_service_bus_message(
        ...     {"request": "data"},
        ...     reply_to="response-queue",
        ...     correlation_id="req-123"
        ... )
        >>> msg.reply_to
        'response-queue'

        Create a message with lock token (peek-lock pattern):

        >>> msg = mock_service_bus_message(
        ...     "Locked message",
        ...     lock_token="lock-abc-123",
        ...     locked_until=datetime.now(UTC) + timedelta(minutes=5)
        ... )
    """
    logger.debug(
        "Creating ServiceBusMessageMock with message_id=%s",
        message_id or "test-message-id",
    )

    # Serialize body if provided
    serialized_body = serialize_to_bytes(body, allow_list=False)

    return ServiceBusMessageMock(
        **filter_none(
            body=serialized_body,
            message_id=message_id,
            session_id=session_id,
            partition_key=partition_key,
            content_type=content_type,
            correlation_id=correlation_id,
            delivery_count=delivery_count,
            enqueued_time_utc=enqueued_time_utc,
            expires_at_utc=expires_at_utc,
            expiration_time=expiration_time,
            dead_letter_source=dead_letter_source,
            dead_letter_reason=dead_letter_reason,
            dead_letter_error_description=dead_letter_error_description,
            locked_until=locked_until,
            lock_token=lock_token,
            sequence_number=sequence_number,
            enqueued_sequence_number=enqueued_sequence_number,
            scheduled_enqueue_time=scheduled_enqueue_time,
            scheduled_enqueue_time_utc=scheduled_enqueue_time_utc,
            label=label,
            subject=subject,
            reply_to=reply_to,
            reply_to_session_id=reply_to_session_id,
            to=to,
            time_to_live=time_to_live,
            state=state,
            transaction_partition_key=transaction_partition_key,
            application_properties=application_properties,
            user_properties=user_properties,
            metadata=metadata,
        )
    )


# =============================================================================
# FACTORY METHODS FOR COMMON SCENARIOS
# =============================================================================


def create_session_message(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    session_id: str = "default-session",
    partition_key: str | None = None,
    **kwargs: Any,
) -> ServiceBusMessageProtocol:
    """Create a Service Bus message for session-aware entities.

    Args:
        body: Message body.
        session_id: Session identifier. Defaults to "default-session".
        partition_key: Partition key (will use session_id if not provided).
        **kwargs: Additional message properties.

    Returns:
        ServiceBusMessageMock configured for session processing.

    Examples:
        >>> msg = create_session_message({"order_id": 123}, session_id="order-session")
        >>> msg.session_id
        'order-session'
    """
    return mock_service_bus_message(
        body,
        session_id=session_id,
        partition_key=partition_key or session_id,
        **kwargs,
    )


def create_dead_letter_message(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    reason: str = "ProcessingError",
    description: str = "Message processing failed after maximum retries",
    source: str = "original-queue",
    delivery_count: int = 10,
    **kwargs: Any,
) -> ServiceBusMessageProtocol:
    """Create a dead-lettered Service Bus message.

    Args:
        body: Message body.
        reason: Dead letter reason. Defaults to "ProcessingError".
        description: Error description.
        source: Source queue/subscription name.
        delivery_count: High delivery count indicating failed processing.
        **kwargs: Additional message properties.

    Returns:
        ServiceBusMessageMock configured as dead-lettered.

    Examples:
        >>> msg = create_dead_letter_message({"failed_data": "test"})
        >>> msg.dead_letter_reason
        'ProcessingError'
        >>> msg.delivery_count
        10
    """
    return mock_service_bus_message(
        body,
        dead_letter_reason=reason,
        dead_letter_error_description=description,
        dead_letter_source=source,
        delivery_count=delivery_count,
        **kwargs,
    )


def create_scheduled_message(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    scheduled_time: datetime | None = None,
    **kwargs: Any,
) -> ServiceBusMessageProtocol:
    """Create a scheduled Service Bus message.

    Args:
        body: Message body.
        scheduled_time: When the message should become available.
            Defaults to 1 hour from now.
        **kwargs: Additional message properties.

    Returns:
        ServiceBusMessageMock configured for scheduled delivery.

    Examples:
        >>> from datetime import datetime, UTC, timedelta
        >>> future_time = datetime.now(UTC) + timedelta(hours=2)
        >>> msg = create_scheduled_message(
        ...     {"reminder": "meeting"}, scheduled_time=future_time
        ... )
        >>> msg.scheduled_enqueue_time_utc == future_time
        True
    """
    if scheduled_time is None:
        scheduled_time = datetime.now(UTC) + timedelta(hours=1)

    return mock_service_bus_message(
        body,
        scheduled_enqueue_time_utc=scheduled_time,
        **kwargs,
    )


def create_request_reply_message(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    correlation_id: str | None = None,
    reply_to: str = "response-queue",
    **kwargs: Any,
) -> ServiceBusMessageProtocol:
    """Create a Service Bus message configured for request-reply pattern.

    Args:
        body: Request message body.
        correlation_id: Correlation ID for tracking request-response.
            Defaults to generated UUID.
        reply_to: Queue/topic name to send replies to.
        **kwargs: Additional message properties.

    Returns:
        ServiceBusMessageMock configured for request-reply.

        >>> msg.reply_to
        'response-queue'
        >>> msg.correlation_id is not None
        True
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())

    return mock_service_bus_message(
        body,
        correlation_id=correlation_id,
        reply_to=reply_to,
        **kwargs,
    )
