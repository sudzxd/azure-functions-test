# Project Style Guide

This document outlines the coding style and conventions for the azure-functions-test project. All contributors and tools (including GitHub Copilot) must adhere to these standards.

---

## General Coding Standards

### PEP 8 Compliance

We use Ruff to enforce PEP compliance throughout the codebase and expect all code to adhere to the following standards:

- Follow [PEP 8](https://peps.python.org/pep-0008/) guidelines for Python code.

### Line Width

- Maximum line width: **88 characters**.
- Use consistent line breaks to maintain readability.

### Indentation

- Use **4 spaces** per indentation level.
- Do not use tabs.

### Spelling Convention

- Use **American English** spellings throughout the codebase (to match Azure Functions SDK conventions).
- Examples of preferred spellings:
  - `behavior` not `behaviour`
  - `initialize` not `initialise`
  - `synchronize` not `synchronise`
  - `serialize` not `serialise`
  - Exception: When referencing Azure Functions SDK classes/methods, use their exact spelling (e.g., `QueueMessage`, `HttpRequest`)

---

## Docstring Style

### General Docstring Guidelines

- All public functions, classes, and modules must have docstrings.
- Use **Google-style** docstrings for documentation.
- Private functions (prefixed with `_`) should have docstrings if their logic is non-trivial.

### Google-Style Docstring Example

```python
def mock_queue_message(
    body: dict | list | str | bytes | None = None,
    *,
    id: str | None = None,
    dequeue_count: int | None = None,
) -> QueueMessageMock:
    """Create a mock QueueMessage for testing.

    Args:
        body: Message body. Dicts/lists are JSON-serialized automatically.
        id: Message ID. Defaults to "test-message-id".
        dequeue_count: Number of times dequeued. Defaults to 1.

    Returns:
        A mock that behaves like azure.functions.QueueMessage.

    Example:
        >>> msg = mock_queue_message({"order_id": 123})
        >>> msg.get_json()
        {'order_id': 123}
    """
    pass
```

**Key Points:**
- There's no need to include type hints again in the docstring, as they are already present in the function signature.
- The function signature is authoritative for types.
- Include examples for public API functions to show typical usage.

---

## Type Hints

### Use Primitive Types Where Available

- Use primitive types (`list`, `dict`, `tuple`, `set`) instead of their `typing` module equivalents.
- Prefer `list[str]` over `List[str]` (Python 3.9+)
- Prefer `dict[str, int]` over `Dict[str, int]` (Python 3.9+)
- Prefer `tuple[str, int]` over `Tuple[str, int]` (Python 3.9+)
- Use `T | None` instead of `Optional[T]` (Python 3.10+)
- Use `str | int` instead of `Union[str, int]` (Python 3.10+)

**Good:**

```python
def process_messages(items: list[str]) -> dict[str, int]:
    """Process list of items and return counts."""
    return {item: len(item) for item in items}

def get_config(name: str) -> dict[str, str] | None:
    """Get config by name, returns None if not found."""
    return None
```

**Avoid:**

```python
from typing import Dict, List, Optional

def process_messages(items: List[str]) -> Dict[str, int]:
    """Process list of items and return counts."""
    return {item: len(item) for item in items}

def get_config(name: str) -> Optional[Dict[str, str]]:
    """Get config by name, returns None if not found."""
    return None
```

### Exception: Use `typing` for Complex Types

Continue using `typing` module for complex type constructs:

- `typing.Any` (no primitive equivalent)
- `typing.TypeVar` (for generics)
- `typing.Generic` (for generic classes)
- `typing.Protocol` (for structural subtyping)
- `typing.Callable[[str], bool]` (function types)

### Minimum Python Version: 3.9

Since we target Python 3.9+:
- Use `list[T]`, `dict[K, V]`, `tuple[T, ...]`, `set[T]`
- For Python 3.10+ features (`|` union syntax), use `from __future__ import annotations` at the top of the file

---

## Type Safety and Data Structures

### Use Dataclasses or Pydantic for Structured Data

**Rule: Always use typed dataclasses instead of raw dictionaries for application data.**

Working with raw dictionaries (`dict[str, Any]`) in application logic is not type-safe and should be avoided. Use strongly-typed dataclasses to ensure:

- Type checking catches errors at development time
- IDE autocomplete and refactoring support
- Clear contracts between components
- Self-documenting code

**Good:**

```python
from dataclasses import dataclass

@dataclass
class MockConfig:
    """Configuration for mock object behaviour."""
    id: str
    dequeue_count: int
    auto_serialize: bool = True

def create_mock(config: MockConfig) -> QueueMessageMock:
    """Create mock with type-safe configuration."""
    return QueueMessageMock(id=config.id, dequeue_count=config.dequeue_count)
```

**Avoid:**

```python
def create_mock(config: dict[str, Any]) -> QueueMessageMock:
    """Create mock without type safety."""
    return QueueMessageMock(id=config["id"], dequeue_count=config["dequeue_count"])
```

### Exception: Azure Functions SDK Compatibility

When interfacing with the Azure Functions SDK, match their API contracts exactly:
- If the SDK expects `dict`, use `dict`
- If the SDK returns `dict`, immediately convert to typed models for internal use

```python
from dataclasses import dataclass
import typing as t

@dataclass
class HttpRequestData:
    """Type-safe representation of HTTP request data."""
    method: str
    url: str
    headers: dict[str, str]

    @classmethod
    def from_sdk_request(cls, request: HttpRequest) -> "HttpRequestData":
        """Convert from SDK type at boundary."""
        return cls(
            method=request.method,
            url=request.url,
            headers=dict(request.headers),
        )
```

---

## Test Naming Conventions

- Test function names must be descriptive and use lowercase with underscores.
- Test names should clearly state the scenario and expected outcome.
- Use the following pattern for test names:

  ```
  test_<unit_of_work>_<scenario>_<expected_result>
  ```

  **Examples:**

  - `test_queue_message_with_dict_body_serializes_to_json`
  - `test_context_output_not_set_raises_value_error`
  - `test_http_mock_with_custom_headers_returns_correct_values`

- Avoid generic names like `test_something` or `test_case1`.
- The test name should make it clear what is being tested and what the expected behavior is.

---

## Module Organization

### Domain-Driven Module Structure

All modules should follow a consistent organization that prioritizes the "need-to-know" principle. Sections are ordered from most important (public API) to least important (implementation details).

#### Recommended Section Order

```python
"""Module docstring describing domain responsibility."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard library
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

# Third-party
from azure.functions import QueueMessage

# Project/local
from .base import BaseMock

# =============================================================================
# TYPES & CONSTANTS
# =============================================================================
DEFAULT_MESSAGE_ID = "test-message-id"
DEFAULT_DEQUEUE_COUNT = 1

# =============================================================================
# PUBLIC API
# =============================================================================
def mock_queue_message(
    body: dict | list | str | bytes | None = None,
    *,
    id: str | None = None,
) -> QueueMessageMock:
    """Create a mock QueueMessage for testing."""
    pass

# =============================================================================
# CORE CLASSES
# =============================================================================
class QueueMessageMock(BaseMock[QueueMessage]):
    """Mock implementation of azure.functions.QueueMessage."""
    pass

# =============================================================================
# PRIVATE HELPERS
# =============================================================================
def _serialize_body(body: dict | list | str | bytes) -> bytes:
    """Convert various body types to bytes."""
    pass
```

#### Rationale

- **Need-to-know**: Readers see the module's interface immediately
- **API-driven**: Public functions define what the module does
- **Top-down reading**: Start with high-level concepts, drill down to implementation
- **Maintainability**: Easy to identify what can be refactored vs what's part of the public contract
- **Consistency**: Same pattern across all domain modules

---

## SOLID Principles in Practice

This library is explicitly designed around SOLID principles:

### Single Responsibility Principle (SRP)
- Each mock class handles **one trigger type** (Queue, HTTP, Timer, etc.)
- `FunctionTestContext` handles **only output capture**, not input mocking
- Factory functions handle **only object creation**, not behavior

### Open/Closed Principle (OCP)
- `BaseMock` provides extension points for new mock types
- New trigger mocks extend `BaseMock` without modifying existing code
- Use abstract methods to enforce contracts

### Liskov Substitution Principle (LSP)
- All mocks are drop-in replacements for real SDK types
- Duck-type compatibility: if `QueueMessage` has a method, our mock has it too
- Clients should not distinguish between real and mock objects

### Interface Segregation Principle (ISP)
- Small, focused interfaces (e.g., `BaseMock._build()`, `BaseMock._default_values()`)
- Clients depend only on methods they use
- No "fat interfaces" with unused methods

### Dependency Inversion Principle (DIP)
- Depend on abstractions (`BaseMock`) not concrete implementations
- High-level modules (tests) don't depend on low-level modules (mock implementations)

---

## Error Handling

### Fail Fast, Fail Clear

- Validate inputs at function entry points
- Raise descriptive exceptions with actionable error messages
- Use built-in exception types when appropriate (`ValueError`, `TypeError`, `KeyError`)

**Good:**

```python
def mock_queue_message(body: dict | None = None) -> QueueMessageMock:
    """Create a mock QueueMessage."""
    if body is not None and not isinstance(body, (dict, list, str, bytes)):
        raise TypeError(
            f"body must be dict, list, str, or bytes, got {type(body).__name__}"
        )
    return QueueMessageMock(body=body)
```

**Avoid:**

```python
def mock_queue_message(body: dict | None = None) -> QueueMessageMock:
    """Create a mock QueueMessage."""
    # Silently coerces or fails later with obscure error
    return QueueMessageMock(body=body)
```

---

## Performance Guidelines

### Optimization Principles

1. **Measure First**: Always profile before optimizing
2. **Lazy Evaluation**: Build mock objects only when accessed (see `BaseMock.build()`)
3. **Reuse Instances**: Cache built mock instances to avoid redundant construction
4. **Simple is Fast**: Prefer straightforward code; complexity rarely pays off in test utilities

### Common Patterns

```python
class BaseMock:
    """Base mock with lazy build pattern."""

    def __init__(self, **overrides: Any) -> None:
        """Initialize with config, but don't build yet."""
        self._values = {**self._default_values(), **overrides}
        self._instance: T | None = None

    def build(self) -> T:
        """Build the mock instance lazily."""
        if self._instance is None:
            self._instance = self._build()
        return self._instance
```

---

## Git Commit Convention

- Use clear, descriptive commit messages
- Follow the format: `<type>: <description>`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**

- `feat: add ServiceBus mock support`
- `fix: handle None body in queue messages`
- `refactor: extract common validation logic to BaseMock`
- `docs: add examples for HTTP mock usage`
- `test: add edge case coverage for context output capture`

---

## Questions?

If you're unsure about any style conventions, check this guide first. When in doubt:
1. Follow PEP 8
2. Prioritize type safety
3. Keep it simple (YAGNI - You Aren't Gonna Need It)
4. Match Azure Functions SDK conventions for compatibility
