# Basic Examples

This directory contains runnable examples showing how to test Azure Functions triggers using `azure-functions-test`.

## Examples

| File                                     | Description                                         |
| ---------------------------------------- | --------------------------------------------------- |
| [`queue_example.py`](./queue_example.py) | Queue Storage trigger with output bindings          |
| [`http_example.py`](./http_example.py)   | HTTP trigger with JSON, form data, and route params |
| [`timer_example.py`](./timer_example.py) | Timer trigger with schedule and past-due handling   |

## Running Examples

Each example file can be run standalone:

```bash
# Run queue example
uv run python examples/basic/queue_example.py

# Run HTTP example
uv run python examples/basic/http_example.py

# Run timer example
uv run python examples/basic/timer_example.py
```

Or run all examples with pytest:

```bash
uv run pytest examples/basic/ -v
```

## Example Output

```bash
Running Queue Storage trigger tests...

✅ test_process_order_queue_success passed
✅ test_process_order_queue_missing_customer passed
✅ test_process_order_queue_with_metadata passed

🎉 All tests passed!
```

## What These Examples Demonstrate

### Queue Example (`queue_example.py`)

- Creating mock queue messages with data
- Testing functions with output bindings
- Accessing message metadata (ID, dequeue count, insertion time)
- Handling JSON message bodies

### HTTP Example (`http_example.py`)

- Testing POST requests with JSON bodies
- Testing POST requests with form data (auto-parsed!)
- Route parameters for RESTful APIs
- Request validation and error responses
- Different HTTP status codes

### Timer Example (`timer_example.py`)

- Testing scheduled functions
- Handling past-due scenarios
- Accessing schedule information
- Testing timer metadata

## Next Steps

After reviewing these examples:

1. Check out the main [README.md](../../README.md) for full API documentation
2. Browse the [tests/unit/](../../tests/unit/) directory for more comprehensive examples
3. Read [ARCHITECTURE.md](../../ARCHITECTURE.md) to understand the design
