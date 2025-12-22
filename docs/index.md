# azure-functions-test

> **Unit test Azure Functions without the runtime.**
<!-- Updated: 2025-12-22 -->

Fast, ergonomic, type-safe mock objects for testing Azure Functions. No runtime, no Azurite, no boilerplate.

[![PyPI version](https://img.shields.io/pypi/v/azure-functions-test.svg)](https://pypi.org/project/azure-functions-test/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-203%20passing-green.svg)](https://github.com/sudzxd/azure-functions-test)
[![Coverage](https://img.shields.io/badge/coverage-75.94%25-brightgreen.svg)](https://github.com/sudzxd/azure-functions-test)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)
[![Type Checked: Pyright](https://img.shields.io/badge/type%20checked-pyright-blue.svg)](https://github.com/microsoft/pyright)

**Requires Python 3.11+** for optimal performance and modern syntax support.

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

## Why This Library?

| Current Approach | Problem |
|-----------------|---------|
| **`func start` + Azurite** | Slow (5-10s startup), flaky, requires Docker |
| **Manual mocking** | Tedious boilerplate, inconsistent across projects |
| **Integration tests only** | Slow feedback loop, hard to test edge cases |
| **No testing** | Bugs in production 🙃 |

**This library fills the gap:** Ergonomic mocks, output capture, zero runtime dependency.

---

## Features

✅ **6 Trigger Types Supported**
- Queue Storage
- HTTP (with form data, JSON, body type auto-detection)
- Timer (with schedule and past-due tracking)
- Blob Storage (with metadata and properties)
- Service Bus (with sessions, dead-letter, correlation)
- Event Grid (with custom and Azure system events)

✅ **Zero Runtime Dependency**
- Pure Python mocks using Pydantic dataclasses
- No `func start` required
- No Azurite or Docker needed
- Tests run in milliseconds, not seconds

✅ **Type-Safe**
- Full Pyright strict mode coverage (0 errors)
- Structural typing with Protocol types
- Auto-complete in VS Code
- Catch errors at test time, not runtime

✅ **SDK-Compatible**
- Drop-in replacements for `azure-functions` types
- All methods and properties work (`get_body()`, `get_json()`, etc.)
- Implements Azure SDK protocols for maximum compatibility

✅ **Minimal Ceremony**
- Simple factory functions with smart defaults
- Only specify data you care about
- Lazy initialization for performance

✅ **Output Capture**
- Explicit output binding capture with `ctx.out("binding_name")`
- Type-safe assertions with `ctx.outputs`
- No magic, full control

---

## Installation

Install from PyPI:

```bash
pip install azure-functions-test
```

For the latest alpha release:
```bash
pip install azure-functions-test==0.1.0a1
```

Or install from source for development:

```bash
git clone https://github.com/sudzxd/azure-functions-test
cd azure-functions-test
uv sync --all-extras
```

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
    mock_blob,
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

## Status

**✅ Full Implementation - 203 Tests Passing**

All 6 core trigger types fully implemented with comprehensive test coverage:
- ✅ Queue Storage mock with Pydantic validation (32 tests)
- ✅ HTTP Request mock with form data support (34 tests)
- ✅ Timer mock with schedule tracking (18 tests)
- ✅ Blob Storage mock with stream support (28 tests)
- ✅ Service Bus mock with complete property coverage (62 tests)
- ✅ Event Grid mock with factory functions (37 tests)

**Metrics:**
- 203 tests passing (+60 comprehensive tests added)
- 75.94% code coverage
- Pyright strict mode: 0 errors
- Complete API documentation with all features

---

## Roadmap

- [x] **Week 1:** Core infrastructure and type system ✅
- [x] **Week 2:** Core mocks (Queue, HTTP, Timer, Blob) ✅
- [x] **Week 3:** Extended mocks (ServiceBus, EventGrid) ✅
- [x] **Week 3:** Documentation and API reference ✅
- [x] **Week 4:** Enhanced features (form data, schedule tracking, factory functions) ✅
- [x] **Week 4:** CI/CD workflows and comprehensive testing ✅
- [ ] **Week 5:** PyPI release preparation ⏳
- [ ] **Week 5:** Advanced features + Cosmos mock
- [ ] **Week 6:** Beta release + community feedback
- [ ] **Post-Launch:** Stable v1.0.0 release

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

| Function | Description |
|----------|-------------|
| `mock_queue_message()` | Create Queue Storage message |
| `mock_http_request()` | Create HTTP request |
| `mock_timer_request()` | Create Timer trigger |
| `mock_blob()` | Create Blob input stream |
| `mock_service_bus_message()` | Create Service Bus message |
| `mock_event_grid_event()` | Create Event Grid event |

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

See inline docstrings for full parameter documentation.

---

## Design Principles

1. **Zero Runtime Dependency** - No Azure Functions runtime or Azurite required
2. **Structural Typing** - Uses Protocol types for duck-typed compatibility with Azure SDK
3. **Minimal Ceremony** - Only specify data you care about, sensible defaults for the rest
4. **Explicit Over Implicit** - Output bindings captured explicitly, no magic
5. **Fail Fast, Fail Clear** - Type errors caught at test time with clear messages

---

## Documentation

- **[API Reference](./api/)** - Complete API documentation
  - [Mocks API](./api/mocks.md) - All 6 mock functions
  - [Context API](./api/context.md) - Output binding capture
  - [Protocols](./api/protocols.md) - Type definitions
- **[Examples](./examples/basic/)** - Working code examples for all triggers
- **[Style Guide](./development/style-guide.md)** - Coding standards for contributors

---

## Contributing

Contributions welcome! See [style-guide.md](./development/style-guide.md) for coding standards.

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

## Tech Stack

- **Python:** 3.11+ (3.11, 3.12, 3.13 supported)
- **Package Management:** [uv](https://github.com/astral-sh/uv)
- **Linting + Formatting:** [Ruff](https://github.com/astral-sh/ruff)
- **Type Checking:** [Pyright](https://github.com/microsoft/pyright) (strict mode)
- **Testing:** pytest + pytest-cov
- **Security:** Bandit + pip-audit
- **CI/CD:** GitHub Actions (coming soon)
- **Documentation:** MkDocs Material (coming soon)

---

## Requirements

- **Python 3.11 or higher** (3.11, 3.12, 3.13)
- **Dependencies:** `azure-functions>=1.17.0`

**Why Python 3.11+?**
- Native `|` union type syntax (cleaner code, no `Optional` imports)
- 25% performance improvement over Python 3.10
- Better error messages and debugging experience
- Modern type system features (Self type, TypeVarTuple, etc.)

---

## License

MIT License

Copyright (c) 2025 Sudarshan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Contact

**Author:** Sudarshan
**Status:** Alpha Release (v0.1.0a1) - [Available on PyPI](https://pypi.org/project/azure-functions-test/)

---

**⭐ Star this repo to follow progress!**
