"""Protocol definitions for Azure Functions trigger types.

This module defines structural type protocols that match the Azure Functions SDK
interfaces. These protocols enable duck typing and proper type checking without
depending on the actual SDK classes.

All protocols are based on the official Azure Functions Python SDK abstract base
classes defined in azure.functions._abc.
"""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from datetime import datetime, timedelta
from typing import Any, Protocol, runtime_checkable

# =============================================================================
# PROTOCOLS
# =============================================================================


@runtime_checkable
class QueueMessageProtocol(Protocol):
    """Structural type for Azure Queue Storage trigger messages.

    This protocol defines the interface for queue messages that Azure Functions
    receives from Queue Storage triggers. Implementations must provide all
    properties and methods defined here.

    Attributes:
        id: Message ID assigned by Queue Storage.
        dequeue_count: Number of times this message has been dequeued.
        expiration_time: UTC datetime when the message expires.
        insertion_time: UTC datetime when message was inserted into queue.
        time_next_visible: UTC datetime when message will be visible next.
        pop_receipt: Token for message operations (delete, update visibility).
    """

    @property
    def id(self) -> str | None:
        """Message ID assigned by Queue Storage."""
        ...

    @property
    def dequeue_count(self) -> int | None:
        """Number of times this message has been dequeued."""
        ...

    @property
    def expiration_time(self) -> datetime | None:
        """UTC datetime when the message expires."""
        ...

    @property
    def insertion_time(self) -> datetime | None:
        """UTC datetime when message was inserted into queue."""
        ...

    @property
    def time_next_visible(self) -> datetime | None:
        """UTC datetime when message will be visible next."""
        ...

    @property
    def pop_receipt(self) -> str | None:
        """Token for message operations (delete, update visibility)."""
        ...

    def get_body(self) -> bytes:
        """Return message content as bytes.

        Returns:
            Message body as bytes.
        """
        ...

    def get_json(self) -> Any:
        """Decode and return message content as a JSON object.

        Returns:
            Decoded JSON data.

        Raises:
            ValueError: When body does not contain valid JSON data.
        """
        ...


@runtime_checkable
class HttpRequestProtocol(Protocol):
    """Structural type for Azure HTTP trigger requests.

    This protocol defines the interface for HTTP requests that Azure Functions
    receives from HTTP triggers.

    Attributes:
        method: HTTP method (GET, POST, PUT, DELETE, etc.).
        url: Full request URL including query string.
        headers: HTTP headers as dictionary.
        params: Query parameters as dictionary.
        route_params: Route parameters from function.json as dictionary.
    """

    @property
    def method(self) -> str:
        """HTTP method (GET, POST, PUT, DELETE, etc.)."""
        ...

    @property
    def url(self) -> str:
        """Full request URL including query string."""
        ...

    @property
    def headers(self) -> dict[str, str]:
        """HTTP headers as dictionary."""
        ...

    @property
    def params(self) -> dict[str, str]:
        """Query parameters as dictionary."""
        ...

    @property
    def route_params(self) -> dict[str, str]:
        """Route parameters from function.json as dictionary."""
        ...

    @property
    def form(self) -> dict[str, str]:
        """Form data parsed from application/x-www-form-urlencoded body."""
        ...

    def get_body(self) -> bytes:
        """Return request body as bytes.

        Returns:
            Request body as bytes.
        """
        ...

    def get_json(self) -> Any:
        """Decode and return request body as a JSON object.

        Returns:
            Decoded JSON data.

        Raises:
            ValueError: When body does not contain valid JSON data.
        """
        ...


@runtime_checkable
class TimerRequestProtocol(Protocol):
    """Structural type for Azure Timer trigger requests.

    This protocol defines the interface for timer trigger requests that Azure
    Functions receives from scheduled timer triggers.

    Attributes:
        past_due: Whether the timer is past its scheduled time.
        schedule_status: Schedule status information dictionary.
        schedule: The timer schedule (e.g., cron expression).
    """

    @property
    def past_due(self) -> bool:
        """Whether the timer is past its scheduled time."""
        ...

    @property
    def schedule_status(self) -> dict[str, Any]:
        """Schedule status information including last/next occurrences."""
        ...

    @property
    def schedule(self) -> dict[str, Any]:
        """Timer schedule configuration."""
        ...


@runtime_checkable
class InputStreamProtocol(Protocol):
    """Structural type for Azure Blob Storage input streams.

    This protocol defines the interface for blob input streams that Azure
    Functions receives from Blob Storage input bindings.

    Attributes:
        name: The name of the blob.
        length: The size of the blob in bytes.
        uri: The blob's primary location URI.
    """

    @property
    def name(self) -> str | None:
        """The name of the blob."""
        ...

    @property
    def length(self) -> int | None:
        """The size of the blob in bytes."""
        ...

    @property
    def uri(self) -> str | None:
        """The blob's primary location URI."""
        ...

    def read(self, size: int = -1) -> bytes:
        """Read blob content.

        Args:
            size: Number of bytes to read. -1 reads entire blob.

        Returns:
            Blob content as bytes.
        """
        ...


@runtime_checkable
class EventGridEventProtocol(Protocol):
    """Structural type for Azure Event Grid events.

    This protocol defines the interface for Event Grid events that Azure
    Functions receives from Event Grid triggers.

    Attributes:
        id: Unique identifier for the event.
        topic: Full resource path to the event source.
        subject: Publisher-defined path to the event subject.
        event_type: One of the registered event types for this event source.
        event_time: UTC time the event was generated.
        data_version: The schema version of the data object.
    """

    @property
    def id(self) -> str:
        """Unique identifier for the event."""
        ...

    @property
    def topic(self) -> str:
        """Full resource path to the event source."""
        ...

    @property
    def subject(self) -> str:
        """Publisher-defined path to the event subject."""
        ...

    @property
    def event_type(self) -> str:
        """One of the registered event types for this event source."""
        ...

    @property
    def event_time(self) -> datetime:
        """UTC time the event was generated."""
        ...

    @property
    def data_version(self) -> str:
        """The schema version of the data object."""
        ...

    def get_json(self) -> Any:
        """Return event data as a JSON object.

        Returns:
            Event data as parsed JSON.
        """
        ...


@runtime_checkable
class ServiceBusMessageProtocol(Protocol):
    """Structural type for Azure Service Bus messages.

    This protocol defines the interface for Service Bus messages that Azure
    Functions receives from Service Bus triggers.

    Attributes:
        message_id: Unique identifier for the message.
        session_id: Session identifier for session-aware entities.
        partition_key: Partition key for partitioned entities.
        content_type: Content type descriptor.
        correlation_id: Correlation identifier.
        delivery_count: Number of times message has been delivered.
        enqueued_time_utc: UTC time when message was enqueued.
        expires_at_utc: UTC time when message expires.
        dead_letter_source: Name of queue/subscription this message was dead lettered.
        dead_letter_reason: Reason for dead lettering.
        dead_letter_error_description: Error description for dead lettering.
        locked_until: UTC time until message is locked in queue.
        lock_token: Lock token for message operations.
        sequence_number: Unique number assigned by Service Bus.
        enqueued_sequence_number: Original sequence number when auto-forwarded.
        application_properties: Application-specific properties.
        user_properties: User-defined properties.
        metadata: Message metadata.
    """

    @property
    def message_id(self) -> str:
        """Unique identifier for the message."""
        ...

    @property
    def session_id(self) -> str | None:
        """Session identifier for session-aware entities."""
        ...

    @property
    def partition_key(self) -> str | None:
        """Partition key for partitioned entities."""
        ...

    @property
    def content_type(self) -> str | None:
        """Content type descriptor."""
        ...

    @property
    def correlation_id(self) -> str | None:
        """Correlation identifier."""
        ...

    @property
    def delivery_count(self) -> int:
        """Number of times message has been delivered."""
        ...

    @property
    def enqueued_time_utc(self) -> datetime:
        """UTC time when message was enqueued."""
        ...

    @property
    def expires_at_utc(self) -> datetime | None:
        """UTC time when message expires."""
        ...

    @property
    def expiration_time(self) -> datetime | None:
        """UTC time when message expires (legacy property)."""
        ...

    @property
    def dead_letter_source(self) -> str | None:
        """Name of queue/subscription this message was dead lettered from."""
        ...

    @property
    def dead_letter_reason(self) -> str | None:
        """Reason for dead lettering."""
        ...

    @property
    def dead_letter_error_description(self) -> str | None:
        """Error description for dead lettering."""
        ...

    @property
    def locked_until(self) -> datetime | None:
        """UTC time until message is locked in queue."""
        ...

    @property
    def lock_token(self) -> str | None:
        """Lock token for message operations."""
        ...

    @property
    def sequence_number(self) -> int | None:
        """Unique number assigned by Service Bus."""
        ...

    @property
    def enqueued_sequence_number(self) -> int | None:
        """Original sequence number when auto-forwarded."""
        ...

    @property
    def scheduled_enqueue_time(self) -> datetime | None:
        """UTC time for scheduled message availability."""
        ...

    @property
    def scheduled_enqueue_time_utc(self) -> datetime | None:
        """UTC time for scheduled message availability (explicit UTC variant)."""
        ...

    @property
    def label(self) -> str | None:
        """Application-specific label."""
        ...

    @property
    def subject(self) -> str | None:
        """Message subject."""
        ...

    @property
    def reply_to(self) -> str | None:
        """Address of queue/topic to reply to."""
        ...

    @property
    def reply_to_session_id(self) -> str | None:
        """Session identifier to reply to."""
        ...

    @property
    def to(self) -> str | None:
        """Destination address."""
        ...

    @property
    def time_to_live(self) -> timedelta | None:
        """Message time to live duration."""
        ...

    @property
    def state(self) -> int | None:
        """Message state."""
        ...

    @property
    def transaction_partition_key(self) -> str | None:
        """Partition key for transactional operations."""
        ...

    @property
    def application_properties(self) -> dict[str, Any]:
        """Application-specific properties."""
        ...

    @property
    def user_properties(self) -> dict[str, Any]:
        """User-defined properties."""
        ...

    @property
    def metadata(self) -> dict[str, Any] | None:
        """Message metadata."""
        ...

    def get_body(self) -> bytes:
        """Return message body as bytes.

        Returns:
            Message body as bytes.
        """
        ...
