"""Example: Testing Event Grid triggered Azure Functions."""

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
from azure_functions_test import FunctionTestContext, mock_event_grid_event
from azure_functions_test.protocols import EventGridEventProtocol


# =============================================================================
# EXAMPLE: Azure Blob Storage Events
# =============================================================================
def handle_blob_created(event: EventGridEventProtocol, output: Out[str]) -> None:
    """Handle BlobCreated event from Azure Storage.

    Args:
        event: Event Grid event for blob creation.
        output: Output binding for processing results.
    """
    event_data = event.get_json()

    result = {
        "event_id": event.id,
        "event_type": event.event_type,
        "blob_url": event_data.get("url"),
        "blob_type": event_data.get("blobType"),
        "content_type": event_data.get("contentType"),
    }

    output.set(json.dumps(result))


def test_handle_blob_created() -> None:
    """Test handling of Blob Storage BlobCreated event."""
    # Arrange
    event = mock_event_grid_event(
        data={
            "api": "PutBlob",
            "clientRequestId": "request-123",
            "requestId": "req-456",
            "eTag": "0x8D4BCC2E4835CD0",
            "contentType": "image/jpeg",
            "contentLength": 1024,
            "blobType": "BlockBlob",
            "url": "https://account.blob.core.windows.net/photos/image.jpg",
        },
        id="blob-event-123",
        event_type="Microsoft.Storage.BlobCreated",
        subject="/blobServices/default/containers/photos/blobs/image.jpg",
    )
    ctx = FunctionTestContext()

    # Act
    handle_blob_created(event, ctx.out("blobCreatedResult"))

    # Assert
    result = json.loads(ctx.outputs["blobCreatedResult"])
    assert result["event_type"] == "Microsoft.Storage.BlobCreated"
    assert result["blob_type"] == "BlockBlob"
    assert "image.jpg" in result["blob_url"]


# =============================================================================
# EXAMPLE: Custom Business Events
# =============================================================================
def handle_order_created(event: EventGridEventProtocol, output: Out[str]) -> None:
    """Handle custom order created event.

    Args:
        event: Event Grid event for order creation.
        output: Output binding for processing results.
    """
    order_data = event.get_json()

    # Process order
    result = {
        "event_id": event.id,
        "order_id": order_data.get("order_id"),
        "customer_id": order_data.get("customer_id"),
        "total": order_data.get("total"),
        "status": "processed",
    }

    output.set(json.dumps(result))


def test_handle_order_created() -> None:
    """Test handling of custom order created event."""
    # Arrange
    event = mock_event_grid_event(
        data={
            "order_id": "ORD-12345",
            "customer_id": "CUST-678",
            "total": 199.99,
            "items": [{"id": 1, "name": "Product A", "price": 199.99}],
        },
        id="order-event-12345",
        event_type="Custom.Order.Created",
        subject="orders/12345",
    )
    ctx = FunctionTestContext()

    # Act
    handle_order_created(event, ctx.out("orderResult"))

    # Assert
    result = json.loads(ctx.outputs["orderResult"])
    assert result["order_id"] == "ORD-12345"
    assert result["customer_id"] == "CUST-678"
    assert result["total"] == 199.99
    assert result["status"] == "processed"


# =============================================================================
# EXAMPLE: Event Type Routing
# =============================================================================
def event_router(event: EventGridEventProtocol, output: Out[str]) -> None:
    """Route events to different handlers based on event type.

    Args:
        event: Event Grid event to route.
        output: Output binding for route destination.
    """
    if event.event_type == "Microsoft.Storage.BlobCreated":
        output.set("blob_handler")
    elif event.event_type == "Microsoft.Storage.BlobDeleted":
        output.set("blob_deletion_handler")
    elif event.event_type.startswith("Custom.Order."):
        output.set("order_handler")
    else:
        output.set("default_handler")


def test_event_routing_blob_created() -> None:
    """Test routing of BlobCreated event."""
    # Arrange
    event = mock_event_grid_event(event_type="Microsoft.Storage.BlobCreated")
    ctx = FunctionTestContext()

    # Act
    event_router(event, ctx.out("route"))

    # Assert
    assert ctx.outputs["route"] == "blob_handler"


def test_event_routing_custom_order() -> None:
    """Test routing of custom order event."""
    # Arrange
    event = mock_event_grid_event(event_type="Custom.Order.Created")
    ctx = FunctionTestContext()

    # Act
    event_router(event, ctx.out("route"))

    # Assert
    assert ctx.outputs["route"] == "order_handler"


# =============================================================================
# EXAMPLE: Event Time Processing
# =============================================================================
def process_event_with_timing(event: EventGridEventProtocol, output: Out[str]) -> None:
    """Process event with timing information.

    Args:
        event: Event Grid event with timestamp.
        output: Output binding for processing results.
    """
    result = {
        "event_id": event.id,
        "event_time": event.event_time.isoformat() if event.event_time else None,
        "processed_at": datetime.now(UTC).isoformat(),
    }

    output.set(json.dumps(result))


def test_process_event_with_custom_time() -> None:
    """Test event processing with custom event time."""
    # Arrange
    custom_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
    event = mock_event_grid_event(
        data={"message": "test"},
        event_time=custom_time,
    )
    ctx = FunctionTestContext()

    # Act
    process_event_with_timing(event, ctx.out("timingResult"))

    # Assert
    result = json.loads(ctx.outputs["timingResult"])
    assert result["event_time"] == "2025-01-15T12:00:00+00:00"


# =============================================================================
# EXAMPLE: Event Metadata
# =============================================================================
def test_event_metadata() -> None:
    """Test Event Grid event metadata properties."""
    # Arrange
    event = mock_event_grid_event(
        data={"test": "data"},
        id="custom-event-123",
        subject="resources/resource-456",
        event_type="Custom.Resource.Updated",
        data_version="2.0",
    )

    # Assert
    assert event.id == "custom-event-123"
    assert event.subject == "resources/resource-456"
    assert event.event_type == "Custom.Resource.Updated"
    assert event.data_version == "2.0"
    assert event.topic.startswith("/subscriptions/")


# =============================================================================
# EXAMPLE: Blob Deleted Event
# =============================================================================
def handle_blob_deleted(event: EventGridEventProtocol, output: Out[str]) -> None:
    """Handle BlobDeleted event from Azure Storage.

    Args:
        event: Event Grid event for blob deletion.
        output: Output binding for processing results.
    """
    event_data = event.get_json()

    result = {
        "event_type": event.event_type,
        "blob_url": event_data.get("url"),
        "api": event_data.get("api"),
        "subject": event.subject,
    }

    output.set(json.dumps(result))


def test_handle_blob_deleted() -> None:
    """Test handling of Blob Storage BlobDeleted event."""
    # Arrange
    event = mock_event_grid_event(
        data={
            "api": "DeleteBlob",
            "requestId": "req-789",
            "contentType": "text/plain",
            "blobType": "BlockBlob",
            "url": "https://account.blob.core.windows.net/docs/file.txt",
        },
        event_type="Microsoft.Storage.BlobDeleted",
        subject="/blobServices/default/containers/docs/blobs/file.txt",
    )
    ctx = FunctionTestContext()

    # Act
    handle_blob_deleted(event, ctx.out("blobDeletedResult"))

    # Assert
    result = json.loads(ctx.outputs["blobDeletedResult"])
    assert result["event_type"] == "Microsoft.Storage.BlobDeleted"
    assert result["api"] == "DeleteBlob"


# =============================================================================
# EXAMPLE: Empty Event Data
# =============================================================================
def test_event_with_empty_data() -> None:
    """Test Event Grid event with empty data."""
    # Arrange
    event = mock_event_grid_event(data={})

    # Assert
    assert event.get_json() == {}


if __name__ == "__main__":
    # Run all test examples
    test_handle_blob_created()
    test_handle_order_created()
    test_event_routing_blob_created()
    test_event_routing_custom_order()
    test_process_event_with_custom_time()
    test_event_metadata()
    test_handle_blob_deleted()
    test_event_with_empty_data()
    print("✓ All Event Grid event examples passed!")
