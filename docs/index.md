# azure-functions-test

> **Unit test Azure Functions without the runtime.**

Fast, ergonomic, type-safe mock objects for testing Azure Functions. No runtime, no Azurite, no boilerplate.

[![PyPI version](https://img.shields.io/pypi/v/azure-functions-test.svg)](https://pypi.org/project/azure-functions-test/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-203%20passing-green.svg)](https://github.com/sudzxd/azure-functions-test)
[![Coverage](https://img.shields.io/badge/coverage-75.94%25-brightgreen.svg)](https://github.com/sudzxd/azure-functions-test)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)
[![Type Checked: Pyright](https://img.shields.io/badge/type%20checked-pyright-blue.svg)](https://github.com/microsoft/pyright)

---

## Quick Example

```python
from azure_functions_test import mock_queue_message, FunctionTestContext

def test_process_order():
    # Arrange
    msg = mock_queue_message({"order_id": 123, "customer": "Alice"})
    ctx = FunctionTestContext()

    # Act
    process_order(msg, ctx.out("result"))

    # Assert
    assert ctx.outputs["result"]["status"] == "completed"
    assert ctx.outputs["result"]["order_id"] == 123
```

---

## Features

- **6 Trigger Types Supported**: Queue Storage, HTTP, Timer, Blob Storage, Service Bus, Event Grid
- **Zero Runtime Dependency**: Pure Python mocks using Pydantic - no `func start`, Azurite, or Docker needed
- **Type-Safe**: Full Pyright strict mode coverage (0 errors) with auto-complete support
- **SDK-Compatible**: Drop-in replacements for `azure-functions` types with all methods and properties
- **Minimal Ceremony**: Simple factory functions with smart defaults - only specify data you care about
- **Output Capture**: Explicit output binding capture with `FunctionTestContext` for type-safe assertions
- **Fast**: Tests run in milliseconds, not seconds

---

## Installation

```bash
pip install azure-functions-test
```

For development:

```bash
git clone https://github.com/sudzxd/azure-functions-test
cd azure-functions-test
uv sync --all-extras
```

---

## Versioning

This package follows **version-compatible versioning** with the `azure-functions` library.

See [CHANGELOG](https://github.com/sudzxd/azure-functions-test/blob/main/CHANGELOG.md) for version history and compatibility details.

**Requirements:**
- Python: `3.11+`
- Azure Functions: `>=1.17.0`
- Pydantic: `>=2.0`

---

## Why This Library?

| Current Approach           | Problem                                           |
| -------------------------- | ------------------------------------------------- |
| **`func start` + Azurite** | Slow (5-10s startup), flaky, requires Docker      |
| **Manual mocking**         | Tedious boilerplate, inconsistent across projects |
| **Integration tests only** | Slow feedback loop, hard to test edge cases       |
| **No testing**             | Bugs in production                                |

**This library fills the gap:** Fast, ergonomic mocks with output capture and zero runtime dependency.

---

## Supported Triggers

### Queue Storage

```python
from azure_functions_test import mock_queue_message

# Simple message
msg = mock_queue_message({"order_id": 123})
assert msg.get_json()["order_id"] == 123

# With metadata
msg = mock_queue_message(
    b"raw data",
    id="msg-456",
    dequeue_count=3,
    insertion_time=datetime(2025, 1, 1, tzinfo=UTC)
)
```

### HTTP Request

```python
from azure_functions_test import mock_http_request

# JSON request
req = mock_http_request(
    method="POST",
    body={"name": "Alice"},
    headers={"Content-Type": "application/json"}
)

# Form data (auto-parsed)
req = mock_http_request(
    method="POST",
    body="name=Alice&age=30",
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
assert req.form["name"] == "Alice"

# With route params
req = mock_http_request(
    url="/api/users/123",
    route_params={"id": "123"}
)
```

### Timer Trigger

```python
from azure_functions_test import mock_timer_request
from datetime import datetime, UTC

# Simple timer
timer = mock_timer_request()

# With schedule and past-due tracking
timer = mock_timer_request(
    schedule={"AdjustForDST": True},
    schedule_status={"Last": datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)},
    past_due=True
)
```

### Blob Storage

```python
from azure_functions_test import mock_blob

# Simple blob
blob = mock_blob(b"file contents", name="data.txt")
assert blob.read() == b"file contents"

# With metadata and properties
blob = mock_blob(
    b"image data",
    name="photo.jpg",
    uri="https://mystorageaccount.blob.core.windows.net/images/photo.jpg",
    metadata={"author": "Alice", "version": "1.0"},
    blob_properties={"ContentType": "image/jpeg"}
)
```

### Service Bus

```python
from azure_functions_test import mock_service_bus_message

# Simple message
msg = mock_service_bus_message({"order_id": 123})
assert msg.get_body() == b'{"order_id": 123}'

# Session-based message
msg = mock_service_bus_message(
    {"step": 1, "data": "workflow"},
    message_id="msg-session-1",
    session_id="workflow-123",
    sequence_number=1
)

# Dead-lettered message
msg = mock_service_bus_message(
    b"failed message",
    dead_letter_source="orders-queue",
    dead_letter_reason="ProcessingException",
    delivery_count=10
)
```

### Event Grid

```python
from azure_functions_test import mock_event_grid_event

# Custom event
event = mock_event_grid_event(
    data={"order_id": 123, "status": "pending"},
    event_type="myapp.order.created",
    subject="orders/123"
)

# Azure system event (Blob Created)
event = mock_event_grid_event(
    data={
        "api": "PutBlob",
        "contentType": "application/json",
        "url": "https://mystorageaccount.blob.core.windows.net/...",
    },
    event_type="Microsoft.Storage.BlobCreated",
    subject="/blobServices/default/containers/data/blobs/file.json",
    topic="/subscriptions/.../storageAccounts/..."
)
```

---

## Output Bindings

Capture output bindings with `FunctionTestContext`:

```python
from azure_functions_test import FunctionTestContext

def test_function_with_output():
    # Arrange
    ctx = FunctionTestContext()

    # Act - pass ctx.out("binding_name") to your function
    my_function(input_data, ctx.out("queue"), ctx.out("blob"))

    # Assert on outputs
    assert ctx.outputs["queue"]["message"] == "processed"
    assert ctx.outputs["blob"] == b"result data"

    # Check if output was set
    assert ctx.is_set("queue")
    assert ctx.is_set("blob")
```

---

## Real-World Example

```python
import azure.functions as func
from azure_functions_test import (
    mock_service_bus_message,
    FunctionTestContext
)

def process_order(msg: func.ServiceBusMessage, blob_out: func.Out[bytes]):
    """Process order from Service Bus and write receipt to Blob."""
    order = msg.get_json()

    # Business logic
    receipt = {
        "order_id": order["order_id"],
        "processed_at": datetime.now(UTC).isoformat(),
        "status": "completed"
    }

    # Write to blob output binding
    blob_out.set(json.dumps(receipt).encode())

# Test
def test_process_order():
    # Arrange
    msg = mock_service_bus_message(
        {"order_id": 12345, "customer_id": 67890},
        message_id="order-12345",
        session_id="customer-67890"
    )
    ctx = FunctionTestContext()

    # Act
    process_order(msg, ctx.out("receipt"))

    # Assert
    receipt = json.loads(ctx.outputs["receipt"])
    assert receipt["order_id"] == 12345
    assert receipt["status"] == "completed"
    assert "processed_at" in receipt
```

---

## API Reference

### Mock Factory Functions

All factory functions follow the same pattern:

```python
mock_<trigger_name>(
    body_or_data,           # Positional: main data
    *,                      # Keyword-only args
    trigger_specific_args   # e.g., message_id, session_id, etc.
)
```

| Function                     | Description                  |
| ---------------------------- | ---------------------------- |
| `mock_queue_message()`       | Create Queue Storage message |
| `mock_http_request()`        | Create HTTP request          |
| `mock_timer_request()`       | Create Timer trigger         |
| `mock_blob()`                | Create Blob input stream     |
| `mock_service_bus_message()` | Create Service Bus message   |
| `mock_event_grid_event()`    | Create Event Grid event      |

See the [API Reference](./api/) for detailed documentation of each function.

### FunctionTestContext

```python
class FunctionTestContext:
    def out(self, name: str) -> Out[T]:
        """Get output binding by name."""

    @property
    def outputs(self) -> dict[str, Any]:
        """Get all captured outputs."""

    def is_set(self, name: str) -> bool:
        """Check if output binding was set."""
```

See the [Context API documentation](./api/context.md) for more details.

---

## Design Principles

1. **Zero Runtime Dependency** - No Azure Functions runtime or Azurite required
2. **Structural Typing** - Uses Protocol types for duck-typed compatibility with Azure SDK
3. **Minimal Ceremony** - Only specify data you care about, sensible defaults for the rest
4. **Explicit Over Implicit** - Output bindings captured explicitly, no magic
5. **Fail Fast, Fail Clear** - Type errors caught at test time with clear messages

---

## Contributing

Contributions welcome! Please read the [Contributing Guide](https://github.com/sudzxd/azure-functions-test/blob/main/CONTRIBUTING.md).

**Development Setup:**

```bash
git clone https://github.com/sudzxd/azure-functions-test
cd azure-functions-test
uv sync --all-extras
PYTHONPATH=src uv run pytest
```

**Run all checks:**

```bash
uv run ruff check .              # Linting
PYTHONPATH=src uv run pyright    # Type checking
PYTHONPATH=src uv run pytest     # Tests with coverage
```

---

## Status

See [CHANGELOG](https://github.com/sudzxd/azure-functions-test/blob/main/CHANGELOG.md) for release history.

- 203 tests passing
- 75.94% code coverage
- Pyright strict mode: 0 errors
- All 6 core trigger types fully implemented

---

## License

Distributed under the MIT License. See [LICENSE](https://github.com/sudzxd/azure-functions-test/blob/main/LICENSE) for more information.

---

## Links

- **Repository**: [github.com/sudzxd/azure-functions-test](https://github.com/sudzxd/azure-functions-test)
- **PyPI**: [pypi.org/project/azure-functions-test](https://pypi.org/project/azure-functions-test/)
- **Issues**: [GitHub Issues](https://github.com/sudzxd/azure-functions-test/issues)

---

**⭐ Star this repo to follow progress!**
