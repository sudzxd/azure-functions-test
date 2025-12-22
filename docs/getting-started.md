# Getting Started

Quick guide to set up and write your first test with `azure-functions-test`.

## Installation

### Development Setup

```bash
git clone https://github.com/sudzxd/azure-functions-test
cd azure-functions-test
uv sync --all-extras
```

### Using in Your Project (Coming Soon)

```bash
pip install azure-functions-test
```

## Your First Test

### 1. Write a Simple Azure Function

```python
# my_function.py
import azure.functions as func

def main(msg: func.QueueMessage) -> None:
    data = msg.get_json()
    print(f"Processing order {data['order_id']}")
```

### 2. Write a Test

```python
# test_my_function.py
from azure_functions_test import mock_queue_message
from my_function import main

def test_process_order():
    # Arrange
    msg = mock_queue_message({"order_id": 123})

    # Act
    main(msg)

    # Assert
    assert msg.get_json()["order_id"] == 123
```

### 3. Run Tests

```bash
pytest test_my_function.py
```

That's it! No runtime, no Azurite, just fast unit tests.

## Testing with Output Bindings

```python
from azure_functions_test import FunctionTestContext, mock_queue_message

def test_with_output():
    # Create test context for output capture
    ctx = FunctionTestContext()
    msg = mock_queue_message({"order_id": 456})

    # Run function
    process_order(msg, ctx)

    # Verify output binding was set
    output = ctx.get_output("receipt_queue")
    assert output["order_id"] == 456
```

## Common Test Patterns

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("status,expected", [
    ("pending", "process"),
    ("cancelled", "skip"),
])
def test_order_statuses(status, expected):
    msg = mock_queue_message({"status": status})
    result = handle_order(msg)
    assert result == expected
```

### Error Handling

```python
def test_invalid_json():
    msg = mock_queue_message("not json")

    with pytest.raises(ValueError):
        process_message(msg)
```

### Edge Cases

```python
def test_poison_message():
    # Simulate message that's been dequeued 6+ times
    msg = mock_queue_message({"data": "test"}, dequeue_count=6)

    result = handle_message(msg)
    assert result["action"] == "move_to_dead_letter"
```

## Next Steps

- **[API Reference](api/index.md)** - Complete documentation for all mocks
- **[Examples](https://github.com/sudzxd/azure-functions-test/tree/main/examples)** - Real-world usage examples
- **[Style Guide](development/style-guide.md)** - Contribution guidelines

## All Available Mocks

| Trigger Type | Mock Function | Documentation |
|-------------|---------------|---------------|
| Queue Storage | `mock_queue_message()` | [Mocks API](api/mocks.md#mock_queue_message) |
| HTTP | `mock_http_request()` | [Mocks API](api/mocks.md#mock_http_request) |
| Timer | `mock_timer_request()` | [Mocks API](api/mocks.md#mock_timer_request) |
| Blob Storage | `mock_blob()` | [Mocks API](api/mocks.md#mock_blob) |
| Service Bus | `mock_service_bus_message()` | [Mocks API](api/mocks.md#mock_service_bus_message) |
| Event Grid | `mock_event_grid_event()` | [Mocks API](api/mocks.md#mock_event_grid_event) |

## Development Commands

```bash
# Run all tests
PYTHONPATH=src pytest

# Type checking
PYTHONPATH=src pyright

# Format code
ruff format .

# Lint
ruff check .
```
