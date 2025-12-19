# API Reference

Complete reference documentation for `azure-functions-test`.

## Quick Navigation

| API Category       | Description                                      | Documentation             |
| ------------------ | ------------------------------------------------ | ------------------------- |
| **Mock Functions** | Create test doubles for Azure Functions triggers | [Mocks API](mocks.md)     |
| **Test Context**   | Capture and assert on output bindings            | [Context API](context.md) |
| **Protocols**      | Type definitions for structural typing           | [Protocols](protocols.md) |

---

## Core Concepts

### Mocks

Mocks are factory functions that create test doubles for Azure Functions trigger inputs. Each mock:

- Returns an object implementing the corresponding Azure SDK protocol
- Accepts flexible input types with automatic serialization
- Provides sensible defaults for all optional parameters
- Is fully type-safe with Pyright strict mode

**Available mocks:**

- `mock_queue_message()` - Queue Storage triggers
- `mock_http_request()` - HTTP triggers
- `mock_timer_request()` - Timer triggers
- `mock_blob()` - Blob Storage triggers
- `mock_service_bus_message()` - Service Bus triggers
- `mock_event_grid_event()` - Event Grid triggers

[→ Full Mock API Reference](mocks.md)

### Test Context

`FunctionTestContext` captures output binding values during test execution, allowing you to:

- Register output bindings with `ctx.out(name)`
- Assert on captured values via `ctx.outputs`
- Check if optional outputs were set with `ctx.is_set(name)`

[→ Full Context API Reference](context.md)

### Protocols

Protocol types provide structural typing for duck-typed mocks. Each protocol defines the interface that Azure Functions expects, allowing our mocks to be drop-in replacements without inheritance.

[→ Full Protocols Reference](protocols.md)

---

## Complete API Index

### Mock Functions

```python
from azure_functions_test import (
    mock_queue_message,
    mock_http_request,
    mock_timer_request,
    mock_blob,
    mock_service_bus_message,
    mock_event_grid_event,
)
```

| Function                                                         | Returns                     | Docs                                   |
| ---------------------------------------------------------------- | --------------------------- | -------------------------------------- |
| `mock_queue_message(body, *, id, dequeue_count, ...)`            | `QueueMessageProtocol`      | [→](mocks.md#mock_queue_message)       |
| `mock_http_request(body, *, method, url, headers, ...)`          | `HttpRequestProtocol`       | [→](mocks.md#mock_http_request)        |
| `mock_timer_request(*, past_due)`                                | `TimerRequestProtocol`      | [→](mocks.md#mock_timer_request)       |
| `mock_blob(content, *, name, uri)`                               | `InputStreamProtocol`       | [→](mocks.md#mock_blob)                |
| `mock_service_bus_message(body, *, message_id, session_id, ...)` | `ServiceBusMessageProtocol` | [→](mocks.md#mock_service_bus_message) |
| `mock_event_grid_event(*, data, id, event_type, ...)`            | `EventGridEventProtocol`    | [→](mocks.md#mock_event_grid_event)    |

### Context Classes

```python
from azure_functions_test import FunctionTestContext, CapturedOutput
```

| Class                 | Purpose                                 | Docs                                |
| --------------------- | --------------------------------------- | ----------------------------------- |
| `FunctionTestContext` | Capture output bindings in tests        | [→](context.md#functiontestcontext) |
| `CapturedOutput[T]`   | Generic output capture with type safety | [→](context.md#capturedoutputt)     |

### Protocol Types

```python
from azure_functions_test.protocols import (
    QueueMessageProtocol,
    HttpRequestProtocol,
    TimerRequestProtocol,
    InputStreamProtocol,
    ServiceBusMessageProtocol,
    EventGridEventProtocol,
)
```

| Protocol                    | Matches Azure SDK Type              | Docs                                        |
| --------------------------- | ----------------------------------- | ------------------------------------------- |
| `QueueMessageProtocol`      | `azure.functions.QueueMessage`      | [→](protocols.md#queuemessageprotocol)      |
| `HttpRequestProtocol`       | `azure.functions.HttpRequest`       | [→](protocols.md#httprequestprotocol)       |
| `TimerRequestProtocol`      | `azure.functions.TimerRequest`      | [→](protocols.md#timerrequestprotocol)      |
| `InputStreamProtocol`       | `azure.functions.InputStream`       | [→](protocols.md#inputstreamprotocol)       |
| `ServiceBusMessageProtocol` | `azure.functions.ServiceBusMessage` | [→](protocols.md#servicebusmessageprotocol) |
| `EventGridEventProtocol`    | `azure.functions.EventGridEvent`    | [→](protocols.md#eventgrideventprotocol)    |

---

## Usage Example

Here's a complete example showing all the main APIs:

```python
from azure_functions_test import (
    mock_queue_message,
    mock_http_request,
    FunctionTestContext,
)


def test_order_processing_pipeline():
    """Test a multi-stage order processing function."""

    # === ARRANGE ===

    # Create mock queue message with order data
    order_msg = mock_queue_message({
        "order_id": 123,
        "customer": "alice@example.com",
        "items": ["laptop", "mouse"],
        "total": 1299.99
    })

    # Create mock HTTP request for webhook notification
    webhook_req = mock_http_request(
        body={"order_id": 123, "status": "processing"},
        method="POST",
        url="https://example.com/webhook",
        headers={"Content-Type": "application/json"}
    )

    # Create test context to capture outputs
    ctx = FunctionTestContext()

    # === ACT ===

    # Call function with mocks
    process_order(
        order_msg,
        ctx.out("processed_orders"),
        ctx.out("customer_notifications"),
        ctx.out("error_log")
    )

    send_webhook(webhook_req, ctx.out("webhook_response"))

    # === ASSERT ===

    # Verify order was processed
    assert ctx.is_set("processed_orders")
    processed = ctx.outputs["processed_orders"]
    assert processed["order_id"] == 123
    assert processed["status"] == "completed"

    # Verify customer was notified
    assert ctx.is_set("customer_notifications")
    notification = ctx.outputs["customer_notifications"]
    assert notification["to"] == "alice@example.com"

    # Verify no errors occurred
    assert not ctx.is_set("error_log")

    # Verify webhook succeeded
    webhook_result = ctx.outputs["webhook_response"]
    assert webhook_result["status_code"] == 200
```

---

## Type Safety

All APIs are fully typed for use with Pyright strict mode:

```python
from azure_functions_test import mock_queue_message
from azure_functions_test.protocols import QueueMessageProtocol

# Type checker knows the return type
msg: QueueMessageProtocol = mock_queue_message({"data": "test"})

# Autocomplete works
data = msg.get_json()  # ✓ Type checker knows this method exists
body = msg.get_body()  # ✓ Returns bytes

# Type errors are caught
msg.invalid_method()  # ✗ Type error: method doesn't exist
```

---

## Next Steps

- [Mock API Reference](mocks.md) - Detailed docs for all mock functions
- [Context API Reference](context.md) - Testing context and output capture
- [Protocols Reference](protocols.md) - Protocol type definitions
- [Testing Guides](../guides/) - Comprehensive testing patterns
- [Examples](../../examples/) - Real-world code samples
