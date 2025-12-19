# Protocols Reference

Protocol types for structural typing in `azure-functions-test`.

## Overview

Protocols define the interfaces that Azure Functions expects for trigger inputs. Our mocks implement these protocols using structural typing (duck typing), allowing them to be drop-in replacements for Azure SDK types without inheritance.

### Why Protocols?

```python
# With protocols, this works:
from azure_functions_test import mock_queue_message
from azure_functions_test.protocols import QueueMessageProtocol

def process_message(msg: QueueMessageProtocol) -> None:
    data = msg.get_json()  # ✓ Type checker knows this exists
    id = msg.id            # ✓ Type checker knows this property

# Mock is structurally compatible:
msg = mock_queue_message({"test": "data"})
process_message(msg)  # ✓ Works! No inheritance needed
```

---

## Available Protocols

| Protocol                    | Azure SDK Type                      | Mock Function                |
| --------------------------- | ----------------------------------- | ---------------------------- |
| `QueueMessageProtocol`      | `azure.functions.QueueMessage`      | `mock_queue_message()`       |
| `HttpRequestProtocol`       | `azure.functions.HttpRequest`       | `mock_http_request()`        |
| `TimerRequestProtocol`      | `azure.functions.TimerRequest`      | `mock_timer_request()`       |
| `InputStreamProtocol`       | `azure.functions.InputStream`       | `mock_blob()`                |
| `ServiceBusMessageProtocol` | `azure.functions.ServiceBusMessage` | `mock_service_bus_message()` |
| `EventGridEventProtocol`    | `azure.functions.EventGridEvent`    | `mock_event_grid_event()`    |

---

## `QueueMessageProtocol`

Structural type for Azure Queue Storage trigger messages.

### Properties

```python
@property
def id(self) -> str | None: ...

@property
def dequeue_count(self) -> int | None: ...

@property
def expiration_time(self) -> datetime | None: ...

@property
def insertion_time(self) -> datetime | None: ...

@property
def time_next_visible(self) -> datetime | None: ...

@property
def pop_receipt(self) -> str | None: ...
```

### Methods

```python
def get_body(self) -> bytes: ...
def get_json(self) -> Any: ...
```

### Example

```python
from azure_functions_test.protocols import QueueMessageProtocol

def process_order(msg: QueueMessageProtocol) -> dict:
    """Process an order from queue message."""
    order = msg.get_json()
    print(f"Processing message {msg.id}, attempt {msg.dequeue_count}")
    return {"status": "processed", "order_id": order["id"]}
```

---

## `HttpRequestProtocol`

Structural type for Azure HTTP trigger requests.

### Properties

```python
@property
def method(self) -> str: ...

@property
def url(self) -> str: ...

@property
def headers(self) -> Mapping[str, str]: ...

@property
def params(self) -> Mapping[str, str]: ...

@property
def route_params(self) -> Mapping[str, str]: ...
```

### Methods

```python
def get_body(self) -> bytes: ...
def get_json(self) -> Any: ...
```

### Example

```python
from azure_functions_test.protocols import HttpRequestProtocol
from azure.functions import HttpResponse

def handle_request(req: HttpRequestProtocol) -> HttpResponse:
    """Handle HTTP request with type safety."""
    if req.method == "POST":
        data = req.get_json()
        return HttpResponse(f"Created: {data}", status_code=201)
    elif req.method == "GET":
        user_id = req.route_params.get("id")
        return HttpResponse(f"User: {user_id}")
    else:
        return HttpResponse("Method not allowed", status_code=405)
```

---

## `TimerRequestProtocol`

Structural type for Azure Timer trigger requests.

### Properties

```python
@property
def past_due(self) -> bool: ...
```

### Example

```python
from azure_functions_test.protocols import TimerRequestProtocol

def scheduled_cleanup(timer: TimerRequestProtocol) -> None:
    """Run scheduled cleanup task."""
    if timer.past_due:
        print("Timer is past due, catching up...")

    # Perform cleanup
    cleanup_old_records()
```

---

## `InputStreamProtocol`

Structural type for Azure Blob Storage input streams.

### Properties

```python
@property
def name(self) -> str | None: ...

@property
def length(self) -> int | None: ...

@property
def uri(self) -> str | None: ...
```

### Methods

```python
def read(self, size: int = -1) -> bytes: ...
```

### Example

```python
from azure_functions_test.protocols import InputStreamProtocol

def process_blob(blob: InputStreamProtocol) -> None:
    """Process blob file with type safety."""
    print(f"Processing {blob.name} ({blob.length} bytes)")

    # Read in chunks
    chunk_size = 4096
    while True:
        chunk = blob.read(chunk_size)
        if not chunk:
            break
        process_chunk(chunk)
```

---

## `ServiceBusMessageProtocol`

Structural type for Azure Service Bus messages.

### Properties

```python
@property
def message_id(self) -> str | None: ...

@property
def session_id(self) -> str | None: ...

@property
def partition_key(self) -> str | None: ...

@property
def content_type(self) -> str | None: ...

@property
def correlation_id(self) -> str | None: ...

@property
def delivery_count(self) -> int | None: ...

@property
def enqueued_time_utc(self) -> datetime | None: ...

@property
def expires_at_utc(self) -> datetime | None: ...

@property
def dead_letter_source(self) -> str | None: ...

@property
def dead_letter_reason(self) -> str | None: ...

@property
def dead_letter_error_description(self) -> str | None: ...

@property
def application_properties(self) -> dict[str, Any] | None: ...

@property
def user_properties(self) -> dict[str, Any] | None: ...
```

### Methods

```python
def get_body(self) -> bytes: ...
def get_json(self) -> Any: ...
```

### Example

```python
from azure_functions_test.protocols import ServiceBusMessageProtocol

def handle_service_bus_message(msg: ServiceBusMessageProtocol) -> None:
    """Handle Service Bus message with session support."""
    data = msg.get_json()

    # Check if message is part of a session
    if msg.session_id:
        print(f"Processing session message: {msg.session_id}")

    # Check delivery count for retry logic
    if msg.delivery_count and msg.delivery_count > 3:
        print(f"Message has been retried {msg.delivery_count} times")

    # Process the message
    process_event(data)
```

---

## `EventGridEventProtocol`

Structural type for Azure Event Grid events.

### Properties

```python
@property
def id(self) -> str | None: ...

@property
def topic(self) -> str | None: ...

@property
def subject(self) -> str | None: ...

@property
def event_type(self) -> str | None: ...

@property
def event_time(self) -> datetime | None: ...

@property
def data_version(self) -> str | None: ...
```

### Methods

```python
def get_json(self) -> dict[str, Any]: ...
```

### Example

```python
from azure_functions_test.protocols import EventGridEventProtocol

def handle_event_grid_event(event: EventGridEventProtocol) -> None:
    """Handle Event Grid event with type safety."""
    print(f"Event type: {event.event_type}")
    print(f"Subject: {event.subject}")

    data = event.get_json()

    # Route based on event type
    if event.event_type == "Microsoft.Storage.BlobCreated":
        handle_blob_created(data)
    elif event.event_type == "MyApp.Order.Created":
        handle_order_created(data)
```

---

## Type Safety Benefits

### Autocomplete

```python
from azure_functions_test import mock_queue_message

msg = mock_queue_message({"test": "data"})

# IDE shows available properties and methods:
msg.id  # ✓ Property exists
msg.get_json()  # ✓ Method exists
msg.invalid_prop  # ✗ Type error
```

### Compile-Time Checks

```python
from azure_functions_test.protocols import QueueMessageProtocol

def process(msg: QueueMessageProtocol) -> None:
    # Type checker validates:
    data = msg.get_json()  # ✓ Returns Any
    count = msg.dequeue_count  # ✓ Returns int | None

    # Type errors caught:
    msg.nonexistent()  # ✗ Error: method doesn't exist
```

### Interchangeability

```python
from azure_functions_test import mock_queue_message
from azure_functions_test.protocols import QueueMessageProtocol

# Function accepts protocol
def process(msg: QueueMessageProtocol) -> None:
    print(msg.get_json())

# Works with mock
mock_msg = mock_queue_message({"test": "data"})
process(mock_msg)  # ✓

# Also works with real Azure SDK type
from azure.functions import QueueMessage
real_msg: QueueMessage = ...
process(real_msg)  # ✓ Structural typing!
```

---

## Advanced Usage

### Generic Type Constraints

```python
from typing import TypeVar
from azure_functions_test.protocols import QueueMessageProtocol

T = TypeVar("T", bound=QueueMessageProtocol)

def batch_process(messages: list[T]) -> list[dict]:
    """Process multiple messages with type safety."""
    return [msg.get_json() for msg in messages]

# Works with any QueueMessageProtocol implementation
mocks = [mock_queue_message({"id": i}) for i in range(10)]
results = batch_process(mocks)  # ✓
```

### Protocol Composition

```python
from typing import Protocol
from azure_functions_test.protocols import QueueMessageProtocol

class ProcessableMessage(Protocol):
    """Extended protocol for messages that can be processed."""
    def get_json(self) -> dict: ...
    @property
    def id(self) -> str | None: ...

def process(msg: ProcessableMessage) -> None:
    """Process any message with get_json and id."""
    data = msg.get_json()
    print(f"Processing {msg.id}: {data}")

# QueueMessageProtocol is compatible (structural subtype)
msg = mock_queue_message({"data": "test"})
process(msg)  # ✓
```

---

## Implementation Notes

### Duck Typing

Protocols use structural subtyping (duck typing), not nominal subtyping:

```python
# This works WITHOUT inheritance:
class MyMock:
    def get_json(self) -> Any:
        return {"custom": "data"}

    def get_body(self) -> bytes:
        return b"data"

    # ... implement all protocol properties/methods

# MyMock implements QueueMessageProtocol without inheriting!
def process(msg: QueueMessageProtocol) -> None:
    print(msg.get_json())

process(MyMock())  # ✓ Works!
```

### Runtime Type Checking

Protocols are checked at static analysis time (Pyright, mypy), not runtime:

```python
from azure_functions_test.protocols import QueueMessageProtocol

msg = mock_queue_message({"data": "test"})

# Static check - always True
isinstance(msg, QueueMessageProtocol)  # ✗ Doesn't work at runtime

# Use static typing instead
def process(msg: QueueMessageProtocol) -> None:  # ✓ Checked by Pyright
    ...
```

---

## See Also

- [Mock API Reference](mocks.md) - Functions that return protocol implementations
- [Context API](context.md) - For capturing function outputs
- [PEP 544](https://peps.python.org/pep-0544/) - Structural subtyping specification
