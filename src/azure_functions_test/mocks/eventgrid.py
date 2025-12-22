"""Event Grid event mock implementation.

This module provides a duck-typed mock for Azure Event Grid events
with Pydantic validation and full type safety.
"""

from __future__ import annotations

import uuid

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from datetime import UTC, datetime
from typing import Any

# Third-party
from pydantic import Field
from pydantic.dataclasses import dataclass

# Project/Local
from .._internal import get_logger
from ..protocols import EventGridEventProtocol
from .base import filter_none

# =============================================================================
# LOGGER
# =============================================================================
logger = get_logger(__name__)


# =============================================================================
# CORE CLASSES
# =============================================================================
@dataclass
class EventGridEventMock:
    """Duck-typed mock for Azure Event Grid events.

    This class implements the EventGridEventProtocol interface using Pydantic
    dataclass for validation and type safety. It provides automatic JSON
    serialization for event data.

    Attributes:
        id: Unique identifier for the event. Defaults to "test-event-id".
        topic: Full resource path to the event source. Defaults to test topic.
        subject: Publisher-defined path to event subject. Defaults to "test/subject".
        event_type: One of the registered event types. Defaults to "Test.Event".
        event_time: UTC time the event was generated. Defaults to current time.
        data_version: Schema version of the data object. Defaults to "1.0".
        data: Event data as dict. Defaults to empty dict.

    Examples:
        Create a storage blob created event:

        >>> event = EventGridEventMock(
        ...     id="abc123",
        ...     event_type="Microsoft.Storage.BlobCreated",
        ...     subject="/blobServices/default/containers/test/blobs/file.txt",
        ...     data={"url": "https://storage.blob.core.windows.net/test/file.txt"}
        ... )
        >>> event.event_type
        'Microsoft.Storage.BlobCreated'
        >>> event.get_json()
        {'url': 'https://storage.blob.core.windows.net/test/file.txt'}
    """

    id: str = Field(default="test-event-id")
    topic: str = Field(
        default="/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.EventGrid/topics/test-topic"
    )
    subject: str = Field(default="test/subject")
    event_type: str = Field(default="Test.Event")
    event_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data_version: str = Field(default="1.0")
    data: dict[str, Any] = Field(default_factory=dict)

    def get_json(self) -> Any:
        """Return event data as a JSON object.

        Returns:
            Event data dictionary.

        Examples:
            >>> event = EventGridEventMock(data={"key": "value"})
            >>> event.get_json()
            {'key': 'value'}
        """
        return self.data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation showing event ID, type, and memory address.

        Examples:
            >>> event = EventGridEventMock(id="evt-123", event_type="Test.Event")
            >>> repr(event)
            "<EventGridEventMock id='evt-123' event_type='Test.Event' at 0x...>"
        """
        return (
            f"<EventGridEventMock id={self.id!r} event_type={self.event_type!r} "
            f"at {hex(id(self))}>"
        )


# =============================================================================
# PUBLIC API
# =============================================================================
def mock_event_grid_event(
    data: dict[str, Any] | None = None,
    *,
    id: str | None = None,  # noqa: A002
    topic: str | None = None,
    subject: str | None = None,
    event_type: str | None = None,
    event_time: datetime | None = None,
    data_version: str | None = None,
) -> EventGridEventProtocol:
    """Create a mock EventGridEvent for testing.

    Provides a test double for Azure Event Grid trigger inputs with
    automatic data handling and sensible defaults. Returns an object
    that implements EventGridEventProtocol.

    Args:
        data: Event data dictionary. Defaults to empty dict.
        id: Unique event identifier. Defaults to "test-event-id".
        topic: Full resource path to event source. Defaults to test topic path.
        subject: Publisher-defined path to event subject. Defaults to "test/subject".
        event_type: Registered event type. Defaults to "Test.Event".
        event_time: UTC time event was generated. Defaults to current time.
        data_version: Schema version of data object. Defaults to "1.0".

    Returns:
        An EventGridEventMock instance implementing EventGridEventProtocol.

    Examples:
        Create a simple custom event:

        >>> event = mock_event_grid_event(
        ...     data={"message": "Hello, Event Grid!"},
        ...     event_type="Custom.Event"
        ... )
        >>> event.get_json()
        {'message': 'Hello, Event Grid!'}

        Create a Blob Storage event:

        >>> event = mock_event_grid_event(
        ...     data={"url": "https://storage.blob.core.windows.net/container/blob.txt"},
        ...     event_type="Microsoft.Storage.BlobCreated",
        ...     subject="/blobServices/default/containers/container/blobs/blob.txt"
        ... )
        >>> event.event_type
        'Microsoft.Storage.BlobCreated'

        Create an event with custom time:

        >>> from datetime import datetime, UTC
        >>> event = mock_event_grid_event(
        ...     data={"value": 42},
        ...     event_time=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        ... )
        >>> event.event_time
        datetime.datetime(2025, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    """
    logger.debug(
        "Creating EventGridEventMock with id=%s, event_type=%s",
        id or "test-event-id",
        event_type or "Test.Event",
    )

    return EventGridEventMock(
        **filter_none(
            data=data,
            id=id,
            topic=topic,
            subject=subject,
            event_type=event_type,
            event_time=event_time,
            data_version=data_version,
        )
    )


# =============================================================================
# FACTORY METHODS FOR COMMON SCENARIOS
# =============================================================================


def create_blob_created_event(
    blob_url: str,
    *,
    container_name: str = "test-container",
    blob_name: str | None = None,
    storage_account: str = "teststorageaccount",
    **kwargs: Any,
) -> EventGridEventProtocol:
    """Create a Blob Storage 'BlobCreated' event.

    Args:
        blob_url: URL of the created blob.
        container_name: Container name.
        blob_name: Blob name (extracted from URL if not provided).
        storage_account: Storage account name.
        **kwargs: Additional event properties.

    Returns:
        EventGridEventMock configured for blob creation.

    Examples:
        >>> event = create_blob_created_event(
        ...     "https://test.blob.core.windows.net/container/file.txt"
        ... )
        >>> event.event_type
        'Microsoft.Storage.BlobCreated'
    """
    if blob_name is None:
        blob_name = blob_url.split("/")[-1]

    return mock_event_grid_event(
        data={
            "api": "PutBlob",
            "clientRequestId": str(uuid.uuid4()),
            "requestId": str(uuid.uuid4()),
            "eTag": f'"0x{uuid.uuid4().hex[:16].upper()}"',
            "contentType": "application/octet-stream",
            "contentLength": 1024,
            "blobType": "BlockBlob",
            "url": blob_url,
            "sequencer": f"{datetime.now().strftime('%Y%m%d%H%M%S')}0000000000000",
        },
        event_type="Microsoft.Storage.BlobCreated",
        subject=f"/blobServices/default/containers/{container_name}/blobs/{blob_name}",
        topic=f"/subscriptions/{uuid.uuid4()}/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/{storage_account}",
        **kwargs,
    )


def create_blob_deleted_event(
    blob_url: str,
    *,
    container_name: str = "test-container",
    blob_name: str | None = None,
    storage_account: str = "teststorageaccount",
    **kwargs: Any,
) -> EventGridEventProtocol:
    """Create a Blob Storage 'BlobDeleted' event.

    Args:
        blob_url: URL of the deleted blob.
        container_name: Container name.
        blob_name: Blob name (extracted from URL if not provided).
        storage_account: Storage account name.
        **kwargs: Additional event properties.

    Returns:
        EventGridEventMock configured for blob deletion.

    Examples:
        >>> event = create_blob_deleted_event(
        ...     "https://test.blob.core.windows.net/container/old-file.txt"
        ... )
        >>> event.event_type
        'Microsoft.Storage.BlobDeleted'
    """
    if blob_name is None:
        blob_name = blob_url.split("/")[-1]

    return mock_event_grid_event(
        data={
            "api": "DeleteBlob",
            "clientRequestId": str(uuid.uuid4()),
            "requestId": str(uuid.uuid4()),
            "contentType": "application/octet-stream",
            "blobType": "BlockBlob",
            "url": blob_url,
            "sequencer": f"{datetime.now().strftime('%Y%m%d%H%M%S')}0000000000000",
        },
        event_type="Microsoft.Storage.BlobDeleted",
        subject=f"/blobServices/default/containers/{container_name}/blobs/{blob_name}",
        topic=f"/subscriptions/{uuid.uuid4()}/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/{storage_account}",
        **kwargs,
    )


def create_custom_event(
    data: dict[str, Any],
    *,
    event_type: str = "Custom.Application.Event",
    subject: str = "custom/event",
    **kwargs: Any,
) -> EventGridEventProtocol:
    """Create a custom application Event Grid event.

    Args:
        data: Custom event data.
        event_type: Custom event type name.
        subject: Event subject path.
        **kwargs: Additional event properties.

    Returns:
        EventGridEventMock configured for custom events.

    Examples:
        >>> event = create_custom_event(
        ...     {"userId": 123, "action": "login"},
        ...     event_type="MyApp.User.Login"
        ... )
        >>> event.event_type
        'MyApp.User.Login'
    """
    return mock_event_grid_event(
        data=data,
        event_type=event_type,
        subject=subject,
        topic=f"/subscriptions/{uuid.uuid4()}/resourceGroups/test-rg/providers/Microsoft.EventGrid/topics/custom-topic",
        **kwargs,
    )
