"""Queue message mock implementation.

This module provides a duck-typed mock for Azure Queue Storage trigger messages
with automatic body serialization, Pydantic validation, and full type safety.
"""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import json
from datetime import UTC, datetime
from typing import Any

# Third-party
from pydantic import Field
from pydantic.dataclasses import dataclass

# Project/Local
from .._internal import get_logger, serialize_to_bytes
from ..protocols import QueueMessageProtocol
from .base import filter_none

# =============================================================================
# LOGGER
# =============================================================================
logger = get_logger(__name__)


# =============================================================================
# CORE CLASSES
# =============================================================================
@dataclass
class QueueMessageMock:
    """Duck-typed mock for Azure Queue Storage trigger messages.

    This class implements the QueueMessageProtocol interface using Pydantic
    dataclass for validation and type safety. It provides automatic JSON
    serialization for dict/list bodies and sensible defaults for testing.

    Attributes:
        id: Message ID assigned by Queue Storage. Defaults to "test-message-id".
        body: Message body as bytes. Automatically serialized from dict/list/str.
        dequeue_count: Number of times dequeued. Defaults to 1.
        expiration_time: UTC datetime when message expires. Defaults to None.
        insertion_time: UTC datetime when inserted. Defaults to current time.
        time_next_visible: UTC datetime when visible next. Defaults to None.
        pop_receipt: Pop receipt token. Defaults to "test-pop-receipt".

    Examples:
        Create a message with dict body (auto-serialized to JSON):

        >>> msg = QueueMessageMock.create({"order_id": 123})
        >>> msg.get_json()
        {'order_id': 123}
        >>> msg.dequeue_count
        1

        Create a message with custom metadata:

        >>> from datetime import datetime, UTC
        >>> msg = QueueMessageMock.create(
        ...     {"data": "test"},
        ...     id="custom-id",
        ...     dequeue_count=5
        ... )
        >>> msg.id
        'custom-id'
        >>> msg.dequeue_count
        5
    """

    id: str | None = Field(default="test-message-id")
    body: bytes = Field(default=b"")
    dequeue_count: int | None = Field(default=1)
    expiration_time: datetime | None = Field(default=None)
    insertion_time: datetime | None = Field(default_factory=lambda: datetime.now(UTC))
    time_next_visible: datetime | None = Field(default=None)
    pop_receipt: str | None = Field(default="test-pop-receipt")

    def get_body(self) -> bytes:
        """Return message content as bytes.

        Returns:
            Message body as bytes.

        Examples:
            >>> msg = QueueMessageMock(body=b"test")
            >>> msg.get_body()
            b'test'
        """
        return self.body

    def get_json(self) -> Any:
        """Decode and return message content as a JSON object.

        Returns:
            Decoded JSON data.

        Raises:
            ValueError: When body does not contain valid JSON data.

        Examples:
            >>> msg = QueueMessageMock(body=b'{"key": "value"}')
            >>> msg.get_json()
            {'key': 'value'}
        """
        try:
            return json.loads(self.body.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in queue message body: {e}") from e
        except UnicodeDecodeError as e:
            msg = f"Unable to decode queue message body as UTF-8: {e}"
            raise ValueError(msg) from e

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation showing class name, ID, and memory address.

        Examples:
            >>> msg = QueueMessageMock(id="msg-123")
            >>> repr(msg)
            "<QueueMessageMock id='msg-123' at 0x...>"
        """
        return f"<QueueMessageMock id={self.id!r} at {hex(id(self))}>"


# =============================================================================
# PUBLIC API
# =============================================================================
def mock_queue_message(
    body: dict[Any, Any] | list[Any] | str | bytes | None = None,
    *,
    id: str | None = None,  # noqa: A002
    dequeue_count: int | None = None,
    expiration_time: datetime | None = None,
    insertion_time: datetime | None = None,
    time_next_visible: datetime | None = None,
    pop_receipt: str | None = None,
) -> QueueMessageProtocol:
    """Create a mock QueueMessage for testing.

    Provides a test double for Azure Queue Storage trigger inputs with
    automatic body serialization and sensible defaults. Returns an object
    that implements QueueMessageProtocol.

    Args:
        body: Message body. Dicts/lists are JSON-serialized automatically.
            Strings are UTF-8 encoded. Bytes are used as-is.
        id: Message ID. Defaults to "test-message-id".
        dequeue_count: Number of times dequeued. Defaults to 1.
        expiration_time: When the message expires. Defaults to None.
        insertion_time: When message was inserted. Defaults to current UTC.
        time_next_visible: When message will be visible. Defaults to None.
        pop_receipt: Pop receipt token. Defaults to "test-pop-receipt".

    Returns:
        A QueueMessageMock instance implementing QueueMessageProtocol.

    Examples:
        Create a message with dict body (auto-serialized to JSON):

        >>> msg = mock_queue_message({"order_id": 123, "status": "pending"})
        >>> msg.get_json()
        {'order_id': 123, 'status': 'pending'}

        Create a message with string body:

        >>> msg = mock_queue_message("Hello, World!")
        >>> msg.get_body().decode()
        'Hello, World!'

        Create a message with bytes body:

        >>> msg = mock_queue_message(b"\\x00\\x01\\x02")
        >>> msg.get_body()
        b'\\x00\\x01\\x02'

        Create a message with custom metadata:

        >>> from datetime import datetime, UTC
        >>> msg = mock_queue_message(
        ...     {"data": "test"},
        ...     id="custom-id",
        ...     dequeue_count=3,
        ...     insertion_time=datetime(2025, 1, 1, tzinfo=UTC)
        ... )
        >>> msg.id
        'custom-id'
        >>> msg.dequeue_count
        3

        Simulate poison message (high dequeue count):

        >>> msg = mock_queue_message({"order_id": 123}, dequeue_count=6)
        >>> msg.dequeue_count > 5
        True
    """
    logger.debug(
        "Creating QueueMessageMock with id=%s, dequeue_count=%s",
        id or "test-message-id",
        dequeue_count or 1,
    )

    # Serialize body if provided
    serialized_body = serialize_to_bytes(body, allow_list=True)

    return QueueMessageMock(
        **filter_none(
            body=serialized_body,
            id=id,
            dequeue_count=dequeue_count,
            expiration_time=expiration_time,
            insertion_time=insertion_time,
            time_next_visible=time_next_visible,
            pop_receipt=pop_receipt,
        )
    )


# =============================================================================
# FACTORY METHODS FOR COMMON SCENARIOS
# =============================================================================


def create_poison_message(
    body: dict[Any, Any] | list[Any] | str | bytes | None = None,
    *,
    dequeue_count: int = 6,
    **kwargs: Any,
) -> QueueMessageProtocol:
    """Create a poison queue message (high dequeue count).

    Args:
        body: Message body.
        dequeue_count: Number of failed processing attempts (>5 = poison).
        **kwargs: Additional message properties.

    Returns:
        QueueMessageMock configured as a poison message.

    Examples:
        >>> msg = create_poison_message({"problematic": "data"})
        >>> msg.dequeue_count > 5
        True
    """
    return mock_queue_message(
        body,
        dequeue_count=dequeue_count,
        **kwargs,
    )


def create_batch_messages(
    bodies: list[dict[Any, Any] | list[Any] | str | bytes],
    **kwargs: Any,
) -> list[QueueMessageProtocol]:
    """Create multiple queue messages for batch processing tests.

    Args:
        bodies: List of message bodies.
        **kwargs: Common properties for all messages.

    Returns:
        List of QueueMessageMock instances.

    Examples:
        >>> messages = create_batch_messages([
        ...     {"id": 1, "data": "first"},
        ...     {"id": 2, "data": "second"}
        ... ])
        >>> len(messages)
        2
    """
    return [
        mock_queue_message(
            body,
            id=f"batch-message-{i}",
            **kwargs,
        )
        for i, body in enumerate(bodies)
    ]
