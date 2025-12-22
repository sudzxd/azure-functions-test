"""Unit tests for EventGridEvent mock."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from datetime import UTC, datetime

# Project/Local
from azure_functions_test import mock_event_grid_event
from azure_functions_test.mocks.eventgrid import (
    create_blob_created_event,
    create_blob_deleted_event,
    create_custom_event,
)


# =============================================================================
# TESTS: Initialization & Defaults
# =============================================================================
def test_mock_event_grid_event_uses_defaults_when_no_args() -> None:
    """mock_event_grid_event() should use default values when called with no args."""
    event = mock_event_grid_event()

    assert event.id == "test-event-id"
    assert event.topic.startswith("/subscriptions/")
    assert event.subject == "test/subject"
    assert event.event_type == "Test.Event"
    assert event.data_version == "1.0"
    assert event.event_time is not None
    assert event.get_json() == {}


def test_mock_event_grid_event_uses_empty_data_by_default() -> None:
    """mock_event_grid_event() should use empty dict for data by default."""
    event = mock_event_grid_event()

    assert event.get_json() == {}


# =============================================================================
# TESTS: Event Data
# =============================================================================
def test_mock_event_grid_event_simple_data() -> None:
    """Simple data dict should be stored correctly."""
    event = mock_event_grid_event(data={"message": "Hello, Event Grid!"})

    assert event.get_json() == {"message": "Hello, Event Grid!"}


def test_mock_event_grid_event_nested_data() -> None:
    """Nested data dict should be stored correctly."""
    data = {
        "user": {"name": "Alice", "email": "alice@example.com"},
        "action": "created",
    }
    event = mock_event_grid_event(data=data)

    assert event.get_json() == data


def test_mock_event_grid_event_empty_data() -> None:
    """Empty data dict should work correctly."""
    event = mock_event_grid_event(data={})

    assert event.get_json() == {}


def test_mock_event_grid_event_none_data_becomes_empty_dict() -> None:
    """None data should become empty dict."""
    event = mock_event_grid_event(data=None)

    assert event.get_json() == {}


# =============================================================================
# TESTS: Event Metadata
# =============================================================================
def test_mock_event_grid_event_custom_id() -> None:
    """Custom ID should override the default."""
    event = mock_event_grid_event(id="custom-event-123")

    assert event.id == "custom-event-123"


def test_mock_event_grid_event_custom_topic() -> None:
    """Custom topic should override the default."""
    topic = (
        "/subscriptions/abc/resourceGroups/rg/providers/"
        "Microsoft.Storage/storageAccounts/account"
    )
    event = mock_event_grid_event(topic=topic)

    assert event.topic == topic


def test_mock_event_grid_event_custom_subject() -> None:
    """Custom subject should override the default."""
    subject = "/blobServices/default/containers/test/blobs/file.txt"
    event = mock_event_grid_event(subject=subject)

    assert event.subject == subject


def test_mock_event_grid_event_custom_event_type() -> None:
    """Custom event_type should override the default."""
    event = mock_event_grid_event(event_type="Microsoft.Storage.BlobCreated")

    assert event.event_type == "Microsoft.Storage.BlobCreated"


def test_mock_event_grid_event_custom_data_version() -> None:
    """Custom data_version should override the default."""
    event = mock_event_grid_event(data_version="2.0")

    assert event.data_version == "2.0"


# =============================================================================
# TESTS: Event Time
# =============================================================================
def test_mock_event_grid_event_default_event_time_is_current() -> None:
    """Default event_time should be current UTC time."""
    event = mock_event_grid_event()

    assert event.event_time is not None
    assert isinstance(event.event_time, datetime)
    assert event.event_time.tzinfo == UTC


def test_mock_event_grid_event_custom_event_time() -> None:
    """Custom event_time should override the default."""
    custom_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    event = mock_event_grid_event(event_time=custom_time)

    assert event.event_time == custom_time


def test_mock_event_grid_event_event_time_with_microseconds() -> None:
    """Event time with microseconds should be preserved."""
    custom_time = datetime(2025, 1, 1, 12, 0, 0, 123456, tzinfo=UTC)
    event = mock_event_grid_event(event_time=custom_time)

    assert event.event_time == custom_time
    assert event.event_time is not None
    assert event.event_time.microsecond == 123456


# =============================================================================
# TESTS: Multiple Instances
# =============================================================================
def test_mock_event_grid_event_multiple_instances_independent() -> None:
    """Multiple event instances should be independent."""
    event1 = mock_event_grid_event(
        data={"order": 1}, id="event-1", event_type="Order.Created"
    )
    event2 = mock_event_grid_event(
        data={"order": 2}, id="event-2", event_type="Order.Updated"
    )

    assert event1.get_json() == {"order": 1}
    assert event2.get_json() == {"order": 2}
    assert event1.id == "event-1"
    assert event2.id == "event-2"
    assert event1.event_type == "Order.Created"
    assert event2.event_type == "Order.Updated"


# =============================================================================
# TESTS: Integration with Real Use Cases - Azure System Events
# =============================================================================
def test_mock_event_grid_event_blob_created_event() -> None:
    """Should support testing Blob Storage BlobCreated events."""
    event = mock_event_grid_event(
        data={
            "api": "PutBlob",
            "clientRequestId": "request-123",
            "requestId": "req-456",
            "eTag": "0x8D4BCC2E4835CD0",
            "contentType": "text/plain",
            "contentLength": 524,
            "blobType": "BlockBlob",
            "url": "https://account.blob.core.windows.net/container/file.txt",
        },
        id="blob-event-123",
        event_type="Microsoft.Storage.BlobCreated",
        subject="/blobServices/default/containers/container/blobs/file.txt",
        topic="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/account",
    )

    assert event.event_type == "Microsoft.Storage.BlobCreated"
    assert event.get_json()["blobType"] == "BlockBlob"
    assert event.subject == "/blobServices/default/containers/container/blobs/file.txt"


def test_mock_event_grid_event_blob_deleted_event() -> None:
    """Should support testing Blob Storage BlobDeleted events."""
    event = mock_event_grid_event(
        data={
            "api": "DeleteBlob",
            "requestId": "req-789",
            "contentType": "image/jpeg",
            "blobType": "BlockBlob",
            "url": "https://account.blob.core.windows.net/photos/image.jpg",
        },
        event_type="Microsoft.Storage.BlobDeleted",
        subject="/blobServices/default/containers/photos/blobs/image.jpg",
    )

    assert event.event_type == "Microsoft.Storage.BlobDeleted"
    assert event.get_json()["api"] == "DeleteBlob"


# =============================================================================
# TESTS: Integration with Real Use Cases - Custom Events
# =============================================================================
def test_mock_event_grid_event_custom_business_event() -> None:
    """Should support testing custom business events."""
    event = mock_event_grid_event(
        data={
            "order_id": "ORD-12345",
            "customer_id": "CUST-678",
            "total": 199.99,
            "items": ["item1", "item2"],
        },
        id="order-event-12345",
        event_type="Custom.Order.Created",
        subject="orders/12345",
        topic="/business/ecommerce",
    )

    assert event.event_type == "Custom.Order.Created"
    assert event.get_json()["order_id"] == "ORD-12345"
    assert event.subject == "orders/12345"


def test_mock_event_grid_event_custom_notification_event() -> None:
    """Should support testing custom notification events."""
    event = mock_event_grid_event(
        data={
            "message": "User signed up",
            "user_id": "user-123",
            "timestamp": "2025-01-01T12:00:00Z",
        },
        event_type="Custom.User.SignedUp",
        subject="users/user-123",
    )

    assert event.event_type == "Custom.User.SignedUp"
    assert event.get_json()["user_id"] == "user-123"


# =============================================================================
# TESTS: Complete Event Configuration
# =============================================================================
def test_mock_event_grid_event_with_all_parameters() -> None:
    """All parameters should work together."""
    custom_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    event = mock_event_grid_event(
        data={"resource": "/subscriptions/sub/resource"},
        id="event-full-12345",
        topic="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.EventGrid/topics/topic",
        subject="resources/resource-123",
        event_type="Custom.Resource.Updated",
        event_time=custom_time,
        data_version="2.0",
    )

    assert event.get_json() == {"resource": "/subscriptions/sub/resource"}
    assert event.id == "event-full-12345"
    assert event.topic.endswith("topics/topic")
    assert event.subject == "resources/resource-123"
    assert event.event_type == "Custom.Resource.Updated"
    assert event.event_time == custom_time
    assert event.data_version == "2.0"


# =============================================================================
# TESTS: Factory Functions - Blob Events
# =============================================================================
def test_create_blob_created_event_basic() -> None:
    """create_blob_created_event() should create BlobCreated event."""
    blob_url = "https://test.blob.core.windows.net/container/file.txt"
    event = create_blob_created_event(blob_url)

    assert event.event_type == "Microsoft.Storage.BlobCreated"
    assert event.get_json()["url"] == blob_url
    assert event.get_json()["api"] == "PutBlob"
    assert event.get_json()["blobType"] == "BlockBlob"


def test_create_blob_created_event_extracts_blob_name_from_url() -> None:
    """Blob name should be extracted from URL if not provided."""
    blob_url = "https://test.blob.core.windows.net/container/my-file.txt"
    event = create_blob_created_event(blob_url)

    assert "my-file.txt" in event.subject


def test_create_blob_created_event_with_custom_container() -> None:
    """Custom container name should be used in subject."""
    blob_url = "https://test.blob.core.windows.net/uploads/file.txt"
    event = create_blob_created_event(blob_url, container_name="uploads")

    assert "/containers/uploads/" in event.subject


def test_create_blob_created_event_with_custom_blob_name() -> None:
    """Custom blob name should override URL extraction."""
    blob_url = "https://test.blob.core.windows.net/container/file.txt"
    event = create_blob_created_event(blob_url, blob_name="custom-name.txt")

    assert "/blobs/custom-name.txt" in event.subject


def test_create_blob_created_event_with_storage_account() -> None:
    """Storage account should be included in topic."""
    blob_url = "https://myaccount.blob.core.windows.net/container/file.txt"
    event = create_blob_created_event(blob_url, storage_account="myaccount")

    assert "/storageAccounts/myaccount" in event.topic


def test_create_blob_created_event_data_structure() -> None:
    """BlobCreated event should have required data fields."""
    blob_url = "https://test.blob.core.windows.net/container/file.txt"
    event = create_blob_created_event(blob_url)

    data = event.get_json()
    assert "api" in data
    assert "clientRequestId" in data
    assert "requestId" in data
    assert "eTag" in data
    assert "contentType" in data
    assert "contentLength" in data
    assert "blobType" in data
    assert "url" in data
    assert "sequencer" in data


def test_create_blob_deleted_event_basic() -> None:
    """create_blob_deleted_event() should create BlobDeleted event."""
    blob_url = "https://test.blob.core.windows.net/container/old-file.txt"
    event = create_blob_deleted_event(blob_url)

    assert event.event_type == "Microsoft.Storage.BlobDeleted"
    assert event.get_json()["url"] == blob_url
    assert event.get_json()["api"] == "DeleteBlob"
    assert event.get_json()["blobType"] == "BlockBlob"


def test_create_blob_deleted_event_extracts_blob_name_from_url() -> None:
    """Blob name should be extracted from URL if not provided."""
    blob_url = "https://test.blob.core.windows.net/container/deleted-file.txt"
    event = create_blob_deleted_event(blob_url)

    assert "deleted-file.txt" in event.subject


def test_create_blob_deleted_event_with_custom_container() -> None:
    """Custom container name should be used in subject."""
    blob_url = "https://test.blob.core.windows.net/archive/file.txt"
    event = create_blob_deleted_event(blob_url, container_name="archive")

    assert "/containers/archive/" in event.subject


def test_create_blob_deleted_event_data_structure() -> None:
    """BlobDeleted event should have required data fields."""
    blob_url = "https://test.blob.core.windows.net/container/file.txt"
    event = create_blob_deleted_event(blob_url)

    data = event.get_json()
    assert "api" in data
    assert "clientRequestId" in data
    assert "requestId" in data
    assert "contentType" in data
    assert "blobType" in data
    assert "url" in data
    assert "sequencer" in data


# =============================================================================
# TESTS: Factory Functions - Custom Events
# =============================================================================
def test_create_custom_event_basic() -> None:
    """create_custom_event() should create custom event."""
    data = {"userId": 123, "action": "login"}
    event = create_custom_event(data, event_type="MyApp.User.Login")

    assert event.event_type == "MyApp.User.Login"
    assert event.get_json() == {"userId": 123, "action": "login"}


def test_create_custom_event_default_event_type() -> None:
    """Custom event should use default event type if not provided."""
    data = {"key": "value"}
    event = create_custom_event(data)

    assert event.event_type == "Custom.Application.Event"


def test_create_custom_event_with_custom_subject() -> None:
    """Custom subject should be used."""
    data = {"orderId": 456}
    event = create_custom_event(data, subject="orders/456/completed")

    assert event.subject == "orders/456/completed"


def test_create_custom_event_default_subject() -> None:
    """Custom event should use default subject if not provided."""
    data = {"test": "data"}
    event = create_custom_event(data)

    assert event.subject == "custom/event"


def test_create_custom_event_with_additional_properties() -> None:
    """Custom event should support additional event properties."""
    data = {"message": "test"}
    event = create_custom_event(
        data,
        event_type="MyApp.Test.Event",
        data_version="2.0",
        id="custom-event-123",
    )

    assert event.event_type == "MyApp.Test.Event"
    assert event.data_version == "2.0"
    assert event.id == "custom-event-123"


def test_create_custom_event_complex_data() -> None:
    """Custom event should handle complex data structures."""
    data = {
        "user": {"id": 123, "name": "Alice"},
        "items": [{"id": 1, "qty": 2}, {"id": 2, "qty": 1}],
        "total": 150.50,
    }
    event = create_custom_event(data, event_type="MyApp.Order.Created")

    event_data = event.get_json()
    assert event_data["user"]["id"] == 123
    assert len(event_data["items"]) == 2
    assert event_data["total"] == 150.50
