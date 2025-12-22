# Mock API Reference

This page documents all available mock functions for Azure Functions triggers.

## Overview

Each mock function creates a test double for an Azure Functions trigger input. All mocks:

- Return objects that implement the corresponding Azure SDK protocol
- Accept flexible input types with automatic serialization
- Provide sensible defaults for optional parameters
- Are fully type-safe with Pyright strict mode

## Available Mocks

| Mock Function                                             | Trigger Type  | Use Case                          |
| --------------------------------------------------------- | ------------- | --------------------------------- |
| [`mock_queue_message()`](#mock_queue_message)             | Queue Storage | Testing queue-triggered functions |
| [`mock_http_request()`](#mock_http_request)               | HTTP          | Testing HTTP-triggered functions  |
| [`mock_timer_request()`](#mock_timer_request)             | Timer         | Testing scheduled functions       |
| [`mock_blob()`](#mock_blob)                               | Blob Storage  | Testing blob-triggered functions  |
| [`mock_service_bus_message()`](#mock_service_bus_message) | Service Bus   | Testing service bus functions     |
| [`mock_event_grid_event()`](#mock_event_grid_event)       | Event Grid    | Testing event grid functions      |

---

## `mock_queue_message()`

Create a mock Queue Storage message.

### `mock_queue_message()` Signature

```python
def mock_queue_message(
    body: dict[Any, Any] | list[Any] | str | bytes | None = None,
    *,
    id: str | None = None,
    dequeue_count: int | None = None,
    expiration_time: datetime | None = None,
    insertion_time: datetime | None = None,
    time_next_visible: datetime | None = None,
    pop_receipt: str | None = None,
) -> QueueMessageProtocol
```

### `mock_queue_message()` Parameters

| Parameter           | Type                                   | Default              | Description                                      |
| ------------------- | -------------------------------------- | -------------------- | ------------------------------------------------ |
| `body`              | `dict \| list \| str \| bytes \| None` | `None`               | Message body. Dicts/lists auto-serialize to JSON |
| `id`                | `str \| None`                          | `"test-message-id"`  | Message ID assigned by Queue Storage             |
| `dequeue_count`     | `int \| None`                          | `1`                  | Number of times the message has been dequeued    |
| `expiration_time`   | `datetime \| None`                     | `None`               | When the message expires                         |
| `insertion_time`    | `datetime \| None`                     | Current UTC time     | When the message was inserted                    |
| `time_next_visible` | `datetime \| None`                     | `None`               | When the message will be visible next            |
| `pop_receipt`       | `str \| None`                          | `"test-pop-receipt"` | Pop receipt token for operations                 |

### `mock_queue_message()` Returns

`QueueMessageProtocol` - A mock queue message implementing the Azure SDK interface.

### `mock_queue_message()` Examples

**Simple JSON message:**

```python
from azure_functions_test import mock_queue_message

msg = mock_queue_message({"order_id": 123, "status": "pending"})
assert msg.get_json() == {"order_id": 123, "status": "pending"}
```

**String message:**

```python
msg = mock_queue_message("Hello, World!")
assert msg.get_body() == b"Hello, World!"
```

**Simulating poison message:**

```python
msg = mock_queue_message(
    {"failed_order": 456},
    dequeue_count=6  # Exceeds typical max retry count
)
if msg.dequeue_count > 5:
    # Move to dead letter queue
    pass
```

---

## `mock_http_request()`

Create a mock HTTP request.

### `mock_http_request()` Signature

```python
def mock_http_request(
    body: dict[Any, Any] | str | bytes | None = None,
    *,
    method: str = "GET",
    url: str = "http://localhost",
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    route_params: dict[str, str] | None = None,
) -> HttpRequestProtocol
```

### `mock_http_request()` Parameters

| Parameter      | Type                           | Default              | Description                                |
| -------------- | ------------------------------ | -------------------- | ------------------------------------------ |
| `body`         | `dict \| str \| bytes \| None` | `None`               | Request body. Dicts auto-serialize to JSON |
| `method`       | `str`                          | `"GET"`              | HTTP method (GET, POST, PUT, DELETE, etc.) |
| `url`          | `str`                          | `"http://localhost"` | Full request URL                           |
| `headers`      | `dict[str, str] \| None`       | `{}`                 | HTTP headers                               |
| `params`       | `dict[str, str] \| None`       | `{}`                 | Query parameters                           |
| `route_params` | `dict[str, str] \| None`       | `{}`                 | Route parameters (e.g., `/users/{id}`)     |

### `mock_http_request()` Returns

`HttpRequestProtocol` - A mock HTTP request implementing the Azure SDK interface.

### `mock_http_request()` Examples

**Simple GET request:**

```python
from azure_functions_test import mock_http_request

req = mock_http_request(
    method="GET",
    url="http://example.com/api/users",
    params={"page": "1", "limit": "10"}
)
assert req.method == "GET"
assert req.params["page"] == "1"
```

**POST with JSON body:**

```python
req = mock_http_request(
    body={"name": "Alice", "email": "alice@example.com"},
    method="POST",
    url="http://example.com/api/users"
)
data = req.get_json()
assert data["name"] == "Alice"
```

**Request with route parameters:**

```python
req = mock_http_request(
    method="GET",
    route_params={"user_id": "123"}
)
user_id = req.route_params["user_id"]
```

**Form data (application/x-www-form-urlencoded):**

```python
req = mock_http_request(
    body=b"name=Alice&age=30&email=alice%40example.com",
    method="POST",
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
# Form data is automatically parsed
assert req.form["name"] == "Alice"
assert req.form["age"] == "30"
assert req.form["email"] == "alice@example.com"
```

> **Note:** The `form` property automatically parses URL-encoded form data when the Content-Type is `application/x-www-form-urlencoded`. Form data is cached for performance.

---

## `mock_timer_request()`

Create a mock timer request.

### `mock_timer_request()` Signature

```python
def mock_timer_request(
    *,
    past_due: bool = False,
    schedule_status: dict[str, Any] | None = None,
    schedule: dict[str, Any] | None = None,
) -> TimerRequestProtocol
```

### `mock_timer_request()` Parameters

| Parameter         | Type                      | Default                          | Description                                       |
| ----------------- | ------------------------- | -------------------------------- | ------------------------------------------------- |
| `past_due`        | `bool`                    | `False`                          | Whether the timer is past its scheduled time      |
| `schedule_status` | `dict[str, Any] \| None`  | Current time info                | Schedule status with Last/Next/LastUpdated times  |
| `schedule`        | `dict[str, Any] \| None`  | `{}`                             | Timer schedule configuration (e.g., cron expression) |

### `mock_timer_request()` Returns

`TimerRequestProtocol` - A mock timer request implementing the Azure SDK interface.

### `mock_timer_request()` Examples

**Normal timer execution:**

```python
from azure_functions_test import mock_timer_request

timer = mock_timer_request()
assert timer.past_due == False
```

**Past due timer:**

```python
timer = mock_timer_request(past_due=True)
if timer.past_due:
    # Handle backlog or skip execution
    pass
```

**Timer with schedule information:**

```python
from datetime import datetime, UTC, timedelta

now = datetime.now(UTC)
timer = mock_timer_request(
    schedule_status={
        "Last": now - timedelta(hours=1),
        "Next": now + timedelta(hours=1),
        "LastUpdated": now
    },
    schedule={"AdjustForDST": True, "Expression": "0 0 */6 * * *"}
)
assert timer.schedule_status["Last"] < timer.schedule_status["Next"]
assert timer.schedule["Expression"] == "0 0 */6 * * *"
```

> **Note:** The `schedule_status` property contains Last/Next/LastUpdated datetimes. The `schedule` property holds timer configuration like cron expressions.

---

## `mock_blob()`

Create a mock Blob Storage input stream.

### `mock_blob()` Signature

```python
def mock_blob(
    content: str | bytes | None = None,
    *,
    name: str | None = None,
    uri: str | None = None,
) -> InputStreamProtocol
```

### `mock_blob()` Parameters

| Parameter | Type                   | Default           | Description                             |
| --------- | ---------------------- | ----------------- | --------------------------------------- |
| `content` | `str \| bytes \| None` | `None`            | Blob content. Strings are UTF-8 encoded |
| `name`    | `str \| None`          | `"test-blob.txt"` | Blob name                               |
| `uri`     | `str \| None`          | Test URI          | Blob's primary location URI             |

### `mock_blob()` Returns

`InputStreamProtocol` - A mock blob input stream implementing the Azure SDK interface.

### `mock_blob()` Examples

**Text file blob:**

```python
from azure_functions_test import mock_blob

blob = mock_blob(
    content="Hello, World!",
    name="greeting.txt"
)
assert blob.read() == b"Hello, World!"
assert blob.length == 13
```

**Binary blob:**

```python
blob = mock_blob(
    content=b"\x89PNG\r\n\x1a\n",
    name="image.png"
)
data = blob.read()
```

**Reading in chunks:**

```python
blob = mock_blob("Hello, World!")
chunk1 = blob.read(5)  # b"Hello"
chunk2 = blob.read(7)  # b", World"
```

---

## `mock_service_bus_message()`

Create a mock Service Bus message.

### `mock_service_bus_message()` Signature

```python
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
) -> ServiceBusMessageProtocol
```

### `mock_service_bus_message()` Parameters

| Parameter                       | Type                           | Default              | Description                                |
| ------------------------------- | ------------------------------ | -------------------- | ------------------------------------------ |
| `body`                          | `dict \| str \| bytes \| None` | `None`               | Message body                               |
| `message_id`                    | `str \| None`                  | `"test-message-id"`  | Unique message identifier                  |
| `session_id`                    | `str \| None`                  | `None`               | Session identifier for stateful processing |
| `partition_key`                 | `str \| None`                  | `None`               | Partition key for ordering                 |
| `content_type`                  | `str \| None`                  | `"application/json"` | MIME type of the message                   |
| `correlation_id`                | `str \| None`                  | `None`               | Correlation identifier                     |
| `delivery_count`                | `int \| None`                  | `1`                  | Number of delivery attempts                |
| `enqueued_time_utc`             | `datetime \| None`             | Current UTC          | When message was enqueued                  |
| `expires_at_utc`                | `datetime \| None`             | `None`               | Message expiration time                    |
| `dead_letter_source`            | `str \| None`                  | `None`               | Original queue if dead-lettered            |
| `dead_letter_reason`            | `str \| None`                  | `None`               | Reason for dead-lettering                  |
| `dead_letter_error_description` | `str \| None`                  | `None`               | Error description                          |
| `application_properties`        | `dict[str, Any] \| None`       | `{}`                 | Application-specific properties            |
| `user_properties`               | `dict[str, Any] \| None`       | `{}`                 | User-defined properties                    |

### `mock_service_bus_message()` Returns

`ServiceBusMessageProtocol` - A mock Service Bus message implementing the Azure SDK interface.

### `mock_service_bus_message()` Examples

**Basic message:**

```python
from azure_functions_test import mock_service_bus_message

msg = mock_service_bus_message(
    {"event": "order.created", "order_id": 123}
)
assert msg.get_json()["event"] == "order.created"
```

**Session-enabled message:**

```python
msg = mock_service_bus_message(
    {"user_id": "alice", "action": "login"},
    session_id="user-alice"
)
```

**Dead letter message:**

```python
msg = mock_service_bus_message(
    {"failed_data": "..."},
    dead_letter_source="orders-queue",
    dead_letter_reason="ProcessingError",
    dead_letter_error_description="Invalid order format"
)
```

---

## `mock_event_grid_event()`

Create a mock Event Grid event.

### `mock_event_grid_event()` Signature

```python
def mock_event_grid_event(
    *,
    data: dict[str, Any] | None = None,
    id: str | None = None,
    topic: str | None = None,
    subject: str | None = None,
    event_type: str | None = None,
    event_time: datetime | None = None,
    data_version: str | None = None,
) -> EventGridEventProtocol
```

### `mock_event_grid_event()` Parameters

| Parameter      | Type                     | Default           | Description                  |
| -------------- | ------------------------ | ----------------- | ---------------------------- |
| `data`         | `dict[str, Any] \| None` | `{}`              | Event data payload           |
| `id`           | `str \| None`            | `"test-event-id"` | Unique event identifier      |
| `topic`        | `str \| None`            | `"/test/topic"`   | Event source topic           |
| `subject`      | `str \| None`            | `"/test/subject"` | Subject/path within topic    |
| `event_type`   | `str \| None`            | `"Test.Event"`    | Event type identifier        |
| `event_time`   | `datetime \| None`       | Current UTC       | When the event occurred      |
| `data_version` | `str \| None`            | `"1.0"`           | Schema version of event data |

### `mock_event_grid_event()` Returns

`EventGridEventProtocol` - A mock Event Grid event implementing the Azure SDK interface.

### `mock_event_grid_event()` Examples

**Blob created event:**

```python
from azure_functions_test import mock_event_grid_event

event = mock_event_grid_event(
    data={
        "url": "https://myaccount.blob.core.windows.net/container/file.txt",
        "contentType": "text/plain"
    },
    event_type="Microsoft.Storage.BlobCreated",
    subject="/blobServices/default/containers/mycontainer/blobs/file.txt"
)
```

**Custom event:**

```python
event = mock_event_grid_event(
    data={"order_id": 123, "total": 99.99},
    event_type="MyApp.Order.Created",
    subject="/orders/123",
    topic="/subscriptions/xyz/resourceGroups/myapp/providers/MyApp/orders"
)
```

### Event Grid Factory Functions

For common Event Grid scenarios, convenience factory functions are available:

#### `create_blob_created_event()`

Create a Blob Storage 'BlobCreated' event with realistic Azure metadata.

```python
from azure_functions_test.mocks.eventgrid import create_blob_created_event

event = create_blob_created_event(
    "https://myaccount.blob.core.windows.net/container/file.txt",
    container_name="uploads",
    storage_account="myaccount"
)
assert event.event_type == "Microsoft.Storage.BlobCreated"
assert event.get_json()["url"] == "https://myaccount.blob.core.windows.net/container/file.txt"
```

**Parameters:**
- `blob_url` (str): URL of the created blob
- `container_name` (str): Container name (default: "test-container")
- `blob_name` (str | None): Blob name (extracted from URL if not provided)
- `storage_account` (str): Storage account name (default: "teststorageaccount")

#### `create_blob_deleted_event()`

Create a Blob Storage 'BlobDeleted' event.

```python
from azure_functions_test.mocks.eventgrid import create_blob_deleted_event

event = create_blob_deleted_event(
    "https://myaccount.blob.core.windows.net/archive/old-file.txt"
)
assert event.event_type == "Microsoft.Storage.BlobDeleted"
```

**Parameters:** Same as `create_blob_created_event()`

#### `create_custom_event()`

Create a custom application Event Grid event.

```python
from azure_functions_test.mocks.eventgrid import create_custom_event

event = create_custom_event(
    data={"userId": 123, "action": "login"},
    event_type="MyApp.User.Login",
    subject="users/123/login"
)
assert event.event_type == "MyApp.User.Login"
assert event.get_json()["userId"] == 123
```

**Parameters:**
- `data` (dict[str, Any]): Custom event data
- `event_type` (str): Custom event type (default: "Custom.Application.Event")
- `subject` (str): Event subject path (default: "custom/event")

---

## See Also

- [Context API](context.md) - For capturing function outputs
- [Protocols](protocols.md) - Protocol definitions for type safety
- [Examples](../../examples/) - Real-world usage examples
