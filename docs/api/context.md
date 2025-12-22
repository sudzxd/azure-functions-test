# Context API Reference

The Context API provides utilities for testing Azure Functions that use output bindings.

## Overview

When testing Azure Functions, you often need to verify what data was written to output bindings (queues, blobs, tables, etc.). The `FunctionTestContext` class captures these outputs so you can assert against them in your tests.

---

## `FunctionTestContext`

A test context for capturing Azure Functions output bindings.

### `FunctionTestContext` Class Definition

```python
class FunctionTestContext:
    """Test context for capturing Azure Functions output bindings."""
```

### `FunctionTestContext` Methods

#### `out(name: str) -> CapturedOutput[Any]`

Register an output binding and return a capture object.

**`out()` Parameters:**

- `name` (`str`): Name of the output binding (matches function.json binding name)

**`out()` Returns:**

- `CapturedOutput[Any]`: An output capture object that records the value when set

**`out()` Example:**

```python
from azure_functions_test import FunctionTestContext

ctx = FunctionTestContext()
output = ctx.out("result")

# Pass to function
my_function(input_data, output)

# Assert on captured value
assert ctx.outputs["result"] == expected_value
```

#### `is_set(name: str) -> bool`

Check if an output binding has been set.

**`is_set()` Parameters:**

- `name` (`str`): Name of the output binding

**`is_set()` Returns:**

- `bool`: `True` if the output was set, `False` otherwise

**`is_set()` Example:**

```python
ctx = FunctionTestContext()
output = ctx.out("optional_output")

my_function(input_data, output)

if ctx.is_set("optional_output"):
    # Output was written
    process_output(ctx.outputs["optional_output"])
else:
    # Output was not written (conditional logic in function)
    pass
```

### `FunctionTestContext` Properties

#### `outputs: dict[str, Any]`

Dictionary containing all captured output values.

**Type:** `dict[str, Any]`

**`outputs` Example:**

```python
ctx = FunctionTestContext()

my_function(
    input_data,
    ctx.out("queue"),
    ctx.out("blob")
)

# Access all outputs
assert ctx.outputs["queue"] == {"message": "processed"}
assert ctx.outputs["blob"] == b"file content"

# Iterate outputs
for name, value in ctx.outputs.items():
    print(f"{name}: {value}")
```

---

## `CapturedOutput[T]`

A generic output capture that records values written by the function.

### `CapturedOutput[T]` Class Definition

```python
@dataclass
class CapturedOutput(Out[T], Generic[T]):
    """Captures output binding values for testing."""
```

### `CapturedOutput[T]` Methods

#### `set(val: T) -> None`

Set the output value (called by the function under test).

**`set()` Parameters:**

- `val` (`T`): The value to write to the output binding

**`set()` Example:**

```python
def process_order(msg: QueueMessage, output: Out[str]) -> None:
    order = msg.get_json()
    result = {"order_id": order["id"], "status": "processed"}
    output.set(json.dumps(result))

# In test:
ctx = FunctionTestContext()
output = ctx.out("result")

process_order(msg, output)

# Output was captured
assert json.loads(ctx.outputs["result"])["status"] == "processed"
```

#### `get() -> T | None`

Get the captured value.

**`get()` Returns:**

- `T | None`: The captured value, or `None` if not set

**`get()` Example:\*\***

```python
output = ctx.out("result")
my_function(input_data, output)

value = output.get()
if value is not None:
    # Output was set
    process(value)
```

---

## Usage Patterns

### Single Output Binding

```python
from azure_functions_test import FunctionTestContext, mock_queue_message

def test_process_message():
    # Arrange
    msg = mock_queue_message({"order_id": 123})
    ctx = FunctionTestContext()

    # Act
    process_message(msg, ctx.out("result"))

    # Assert
    assert ctx.outputs["result"]["order_id"] == 123
    assert ctx.outputs["result"]["status"] == "completed"
```

### Multiple Output Bindings

```python
def test_multi_output_function():
    ctx = FunctionTestContext()

    my_function(
        input_data,
        ctx.out("queue"),
        ctx.out("blob"),
        ctx.out("table")
    )

    # All outputs captured
    assert ctx.outputs["queue"] is not None
    assert ctx.outputs["blob"] is not None
    assert ctx.outputs["table"] is not None
```

### Conditional Outputs

```python
def test_conditional_output():
    ctx = FunctionTestContext()

    # Function only writes to error output on failure
    process_with_validation(
        invalid_input,
        ctx.out("success"),
        ctx.out("error")
    )

    # Check which output was set
    assert not ctx.is_set("success")
    assert ctx.is_set("error")
    assert "validation failed" in ctx.outputs["error"]
```

### Type-Safe Outputs

```python
from typing import TypedDict

class OrderOutput(TypedDict):
    order_id: int
    status: str
    total: float

def test_typed_output():
    ctx = FunctionTestContext()
    output: CapturedOutput[OrderOutput] = ctx.out("order")

    process_order(input_msg, output)

    # Type checker knows the structure
    result = ctx.outputs["order"]
    assert result["order_id"] == 123
    assert result["status"] == "completed"
```

### Testing Error Handling

```python
def test_error_output():
    ctx = FunctionTestContext()

    try:
        faulty_function(bad_input, ctx.out("result"))
    except ValueError:
        pass  # Expected

    # Verify no output was written before error
    assert not ctx.is_set("result")
```

---

## Integration with Azure Functions

The context API is designed to work seamlessly with Azure Functions signatures:

### Queue Trigger Example

```python
# Function code
import azure.functions as func

def main(msg: func.QueueMessage, result: func.Out[str]) -> None:
    data = msg.get_json()
    processed = process_data(data)
    result.set(json.dumps(processed))

# Test code
def test_main():
    from azure_functions_test import mock_queue_message, FunctionTestContext

    msg = mock_queue_message({"user": "alice"})
    ctx = FunctionTestContext()

    main(msg, ctx.out("result"))

    output = json.loads(ctx.outputs["result"])
    assert output["user"] == "alice"
```

### HTTP Trigger Example

```python
# Function code
def main(req: func.HttpRequest, msg: func.Out[str]) -> func.HttpResponse:
    name = req.params.get("name")
    msg.set(f"Processed request from {name}")
    return func.HttpResponse(f"Hello, {name}!")

# Test code
def test_main():
    from azure_functions_test import mock_http_request, FunctionTestContext

    req = mock_http_request(params={"name": "Alice"})
    ctx = FunctionTestContext()

    response = main(req, ctx.out("msg"))

    assert response.status_code == 200
    assert ctx.outputs["msg"] == "Processed request from Alice"
```

---

## Best Practices

### 1. Use Descriptive Output Names

```python
# Good
ctx.out("processed_orders")
ctx.out("error_log")
ctx.out("notification_queue")

# Avoid
ctx.out("out1")
ctx.out("output")
ctx.out("result")
```

### 2. Check Output Before Accessing

```python
# Safe
if ctx.is_set("optional_output"):
    value = ctx.outputs["optional_output"]

# Risky - may raise KeyError
value = ctx.outputs["optional_output"]
```

### 3. Type Annotations

```python
# Type-safe
output: CapturedOutput[dict[str, Any]] = ctx.out("result")

# Less safe
output = ctx.out("result")
```

### 4. Clear Test Arrangement

```python
def test_function():
    # Arrange - setup inputs and context
    msg = mock_queue_message(test_data)
    ctx = FunctionTestContext()

    # Act - call function
    my_function(msg, ctx.out("result"))

    # Assert - verify outputs
    assert ctx.outputs["result"] == expected
```

---

## See Also

- [Mock API Reference](mocks.md) - For creating test inputs
- [Examples](../../examples/) - Real-world usage examples
