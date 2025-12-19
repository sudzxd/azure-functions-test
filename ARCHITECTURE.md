# Project Architecture & Implementation Plan

**Project:** azure-functions-test
**Version:** 0.1.0 (Alpha)
**Last Updated:** 2025-12-19
**Python Version:** 3.11+ (3.11, 3.12, 3.13 supported)

> **Note:** Python 3.11+ is required for native union type syntax (`|`), improved performance, and better error messages. Python 3.9 and 3.10 are not supported.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Design Principles](#design-principles)
4. [Architecture Overview](#architecture-overview)
5. [Component Specifications](#component-specifications)
6. [Implementation Phases](#implementation-phases)
7. [Quality Assurance](#quality-assurance)
8. [Technology Stack](#technology-stack)
9. [Success Metrics](#success-metrics)

---

## Executive Summary

**azure-functions-test** is a Python library that provides ergonomic, type-safe mock objects for testing Azure Functions without requiring the full Functions runtime or Azurite emulator.

**Key Value Proposition:**

- Fast, focused unit tests (no runtime overhead)
- Minimal ceremony (simple factory functions)
- Type-safe (strict Pyright checks, full type coverage)
- SDK-compatible (drop-in replacements for real Azure Functions types)

**Target Audience:**

- Python developers building Azure Functions
- Teams wanting fast CI/CD pipelines
- Projects requiring comprehensive unit test coverage

---

## Problem Statement

### Current Testing Landscape

| Approach                                  | Strengths                              | Weaknesses                                                  |
| ----------------------------------------- | -------------------------------------- | ----------------------------------------------------------- |
| **Full Runtime (`func start` + Azurite)** | High fidelity, tests real integrations | Slow (5-10s startup), flaky, requires Docker/local emulator |
| **Manual Mocks**                          | Fast, focused                          | Tedious boilerplate, inconsistent across projects           |
| **No Testing**                            | None                                   | Bugs in production, slow feedback cycles                    |

### Gap Analysis

**What's Missing:**

- A standardized library for Azure Functions mocking
- Type-safe mock objects that match the SDK API
- Output binding capture for assertions
- Zero-dependency test setup (no runtime required)

**Why Existing Solutions Fall Short:**

- **unittest.mock.Mock**: Too generic, no type safety, no Azure-specific helpers
- **pytest-mock**: Same limitations as unittest.mock
- **Azure Functions Runtime**: Overkill for unit tests, slow, integration-level

---

## Design Principles

### 1. Zero Runtime Dependency

**Principle:** Tests using this library must not require the Azure Functions runtime, Azurite, or any external services. Everything is in-memory.

**Implementation:**

- Mock objects are pure Python, no subprocess calls
- No network I/O, no file I/O (except for test fixtures)
- All state is ephemeral and isolated per test

### 2. Duck-Type Compatibility

**Principle:** All mock objects must be usable as drop-in replacements for real SDK types. If `azure.functions.QueueMessage` has a method, our mock has it too.

**Implementation:**

- Match SDK method signatures exactly
- Implement all public methods from SDK types
- Delegate attribute access via `__getattr__` for complete compatibility

### 3. Minimal Ceremony

**Principle:** Creating a mock should require only the data you care about. Sensible defaults for everything else.

**Implementation:**

- Factory functions with keyword-only arguments
- Smart defaults (e.g., `id="test-message-id"`, `dequeue_count=1`)
- Automatic serialization (dicts → JSON, strings → bytes)

### 4. Explicit Over Implicit

**Principle:** Output bindings are captured explicitly via `ctx.out("name")`. No magic interception of function calls.

**Implementation:**

- `FunctionTestContext.out()` returns a `CapturedOutput` object
- Functions set output via `output.set(value)`
- Tests assert via `ctx.outputs["name"]` or `ctx.assert_output("name", expected)`

### 5. Fail Fast, Fail Clear

**Principle:** Type errors caught at test time, not runtime. Clear error messages when mocks are misconfigured.

**Implementation:**

- Strict type checking (Pyright in strict mode)
- Descriptive error messages with actionable feedback
- Input validation at function entry points

### 6. Open/Closed Principle (OCP)

**Principle:** New mock types extend `BaseMock` without modifying existing code.

**Implementation:**

- Abstract base class `BaseMock[T]` with template method pattern
- Subclasses implement `_build()` and `_default_values()`
- Factory functions provide ergonomic API

### 7. Single Responsibility Principle (SRP)

**Principle:** Each component has one job.

**Implementation:**

- Mocks create test doubles (nothing else)
- Context captures outputs (nothing else)
- Assertions verify results (nothing else)

### 8. DRY (Don't Repeat Yourself)

**Principle:** Common mock logic lives in `BaseMock`. Trigger-specific logic only in subclasses.

**Implementation:**

- `BaseMock` handles lazy initialization, default merging, delegation
- Subclasses only implement trigger-specific logic
- No duplicated validation or construction code

---

## Architecture Overview

### High-Level Component Diagram

```bash
┌─────────────────────────────────────────────────────────────────┐
│                        User Test Code                           │
│  test_my_function.py                                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ from azure_functions_test import mock_queue_message, ...   │ │
│  │                                                            │ │
│  │ def test_process_order():                                  │ │
│  │     msg = mock_queue_message({"order_id": 123})            │ │
│  │     ctx = FunctionTestContext()                            │ │
│  │     process_order(msg, ctx.out("result"))                  │ │
│  │     assert ctx.outputs["result"]["status"] == "completed"  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ imports
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              azure_functions_test (Public API)                  │
│  __init__.py                                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ # Public exports                                           │ │
│  │ from .mocks import (                                       │ │
│  │     mock_queue_message,                                    │ │
│  │     mock_http_request,                                     │ │
│  │     mock_timer_trigger,                                    │ │
│  │     ...                                                    │ │
│  │ )                                                          │ │
│  │ from .context import FunctionTestContext                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   mocks/         │ │   context.py     │ │   assertions/    │
│                  │ │                  │ │                  │
│ • base.py        │ │ FunctionTest     │ │ • matchers.py    │
│ • queue.py       │ │ Context          │ │                  │
│ • http.py        │ │                  │ │ Custom pytest    │
│ • timer.py       │ │ CapturedOutput   │ │ matchers         │
│ • blob.py        │ │                  │ │                  │
│ • servicebus.py  │ └──────────────────┘ └──────────────────┘
│ • eventgrid.py   │
│ • cosmos.py      │
└──────────────────┘
         │
         │ extends
         ▼
┌──────────────────┐
│   BaseMock[T]    │
│                  │
│ Generic base     │
│ class for all    │
│ mock types       │
└──────────────────┘
         │
         │ interfaces with
         ▼
┌──────────────────┐
│ azure.functions  │
│                  │
│ SDK types        │
│ (external dep)   │
└──────────────────┘
```

### Layer Responsibilities

| Layer          | Responsibility                       | Dependencies               |
| -------------- | ------------------------------------ | -------------------------- |
| **Public API** | Export user-facing functions/classes | mocks, context, assertions |
| **Mocks**      | Create test doubles for triggers     | base, azure.functions      |
| **Context**    | Capture output bindings              | None (pure Python)         |
| **Assertions** | Custom matchers for pytest           | context, pytest (optional) |
| **Base**       | Abstract mock interface              | typing, abc                |

---

## Component Specifications

### 1. BaseMock (mocks/base.py)

**Purpose:** Abstract base class providing common mock infrastructure.

**Responsibilities:**

- Generic type parameter `T` for SDK type
- Lazy initialization (build on first access)
- Default value merging
- Attribute delegation to built instance

**Interface:**

```python
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

T = TypeVar("T")

class BaseMock(ABC, Generic[T]):
    """Base class for all Azure Functions mocks."""

    @abstractmethod
    def _build(self) -> T:
        """Build the mock object. Implemented by subclasses."""
        ...

    @classmethod
    @abstractmethod
    def _default_values(cls) -> dict[str, Any]:
        """Return default values for optional fields."""
        ...

    def build(self) -> T:
        """Public method to get the built instance."""
        if self._instance is None:
            self._instance = self._build()
        return self._instance
```

**Design Decisions:**

- Generic `T` ensures type safety (subclasses specify concrete SDK type)
- Template method pattern: `_build()` and `_default_values()` are extension points
- Lazy initialization avoids unnecessary construction
- `__getattr__` delegation makes mocks transparent to user code

---

### 2. Queue Mock (mocks/queue.py)

**Purpose:** Mock implementation of `azure.functions.QueueMessage`.

**Responsibilities:**

- Accept dict/list/str/bytes as body
- Auto-serialize dicts/lists to JSON
- Provide sensible defaults for all fields
- Match SDK API exactly

**Public API:**

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
    """
```

**Implementation Notes:**

- Extends `BaseMock[QueueMessage]`
- `_build()` constructs real `QueueMessage` from SDK
- `_default_values()` returns dict with sensible test defaults
- Body serialization logic in private `_serialize_body()` helper

---

### 3. HTTP Mock (mocks/http.py)

**Purpose:** Mock implementation of `azure.functions.HttpRequest`.

**Public API:**

```python
def mock_http_request(
    method: str = "GET",
    url: str = "http://localhost/api/test",
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    body: bytes | str | dict | None = None,
) -> HttpRequestMock:
    """Create a mock HttpRequest for testing."""
```

**Key Features:**

- Supports all HTTP methods
- Auto-serializes dict body to JSON
- Merges headers/params with defaults
- Route parameters support

---

### 4. FunctionTestContext (context.py)

**Purpose:** Capture output bindings during function execution.

**Responsibilities:**

- Create named output captures via `out(name)`
- Store output values set by function
- Provide assertion helpers

**Public API:**

```python
class FunctionTestContext:
    """Captures output bindings during function execution."""

    def out(self, name: str) -> CapturedOutput[Any]:
        """Create a named output binding capture."""

    @property
    def outputs(self) -> dict[str, Any]:
        """Get all captured output values."""

    def assert_output(self, name: str, expected: Any) -> None:
        """Assert an output binding has a specific value."""
```

**Usage Pattern:**

```python
def test_my_function():
    ctx = FunctionTestContext()
    my_function(input_data, ctx.out("result"))

    # Assert via dict access
    assert ctx.outputs["result"] == expected

    # Or via helper
    ctx.assert_output("result", expected)
```

---

### 5. Additional Mocks (Phases 2-4)

| Mock           | SDK Type            | Phase | Key Features                         |
| -------------- | ------------------- | ----- | ------------------------------------ |
| **Timer**      | `TimerRequest`      | 1     | Past due flag, schedule info         |
| **Blob**       | `InputStream`       | 1     | Blob metadata, URI, size             |
| **ServiceBus** | `ServiceBusMessage` | 2     | Message ID, session ID, properties   |
| **EventGrid**  | `EventGridEvent`    | 2     | Event type, subject, data            |
| **Cosmos**     | `Document`          | 3     | Document ID, partition key, metadata |

---

## Implementation Phases

### Phase 1: Core Foundation (Week 1-2)

**Goal:** Establish project infrastructure and core mocks.

**Deliverables:**

1. Project setup

   - [x] Create project folder structure
   - [ ] Initialize uv project (`uv init`)
   - [ ] Configure pyproject.toml with all dependencies
   - [ ] Set up Ruff, Pyright, pytest configs
   - [ ] Create STYLE_GUIDE.md
   - [ ] Create ARCHITECTURE.md

2. Core components

   - [ ] Implement `BaseMock` abstract class
   - [ ] Implement `FunctionTestContext` and `CapturedOutput`
   - [ ] Implement `QueueMessageMock` + factory function
   - [ ] Implement `HttpRequestMock` + factory function
   - [ ] Implement `TimerRequestMock` + factory function
   - [ ] Implement `BlobMock` + factory function

3. Testing

   - [ ] Unit tests for `BaseMock` behavior
   - [ ] Unit tests for each mock type
   - [ ] Unit tests for `FunctionTestContext`
   - [ ] Achieve >90% coverage

4. Documentation
   - [ ] README.md with quickstart
   - [ ] API documentation stubs
   - [ ] Example usage in `/examples/basic/`

**Success Criteria:**

- All tests pass on Python 3.9, 3.10, 3.11, 3.12
- Pyright strict mode passes with zero errors
- Ruff linting passes with zero errors
- Test coverage >90%

---

### Phase 2: Extended Triggers (Week 3)

**Goal:** Add support for ServiceBus and EventGrid triggers.

**Deliverables:**

1. ServiceBus mock

   - [ ] `ServiceBusMessageMock` implementation
   - [ ] Factory function with message properties, session ID
   - [ ] Unit tests with >90% coverage

2. EventGrid mock

   - [ ] `EventGridEventMock` implementation
   - [ ] Factory function with event type, subject, data
   - [ ] Unit tests with >90% coverage

3. Examples
   - [ ] ServiceBus processing example
   - [ ] EventGrid handler example

**Success Criteria:**

- Same quality gates as Phase 1
- Documentation updated with new mock types

---

### Phase 3: CI/CD & Release Infrastructure (Week 4)

**Goal:** Automate quality checks and set up release pipeline.

**Deliverables:**

1. GitHub Actions workflows

   - [ ] `.github/workflows/ci.yml` (lint, typecheck, test, security)
   - [ ] `.github/workflows/release.yml` (build, publish to PyPI)
   - [ ] Matrix testing across Python versions

2. Release automation

   - [ ] Configure Hatch for versioning from git tags
   - [ ] Set up git-cliff for changelog generation
   - [ ] Configure PyPI trusted publishing
   - [ ] Create PyPI environments (pypi, pypi-prerelease)

3. Documentation site

   - [ ] Set up MkDocs with Material theme
   - [ ] Configure mkdocstrings for API docs
   - [ ] Write user guides (getting started, testing patterns, CI integration)
   - [ ] Deploy to GitHub Pages

4. Community infrastructure
   - [ ] Issue templates (bug report, feature request)
   - [ ] Pull request template
   - [ ] CONTRIBUTING.md
   - [ ] CODEOWNERS

**Success Criteria:**

- CI runs on every PR and passes
- Alpha release published to PyPI
- Documentation site live and accessible
- All community templates in place

---

### Phase 4: Advanced Features (Week 5-6)

**Goal:** Add remaining mock types and advanced testing utilities.

**Deliverables:**

1. Cosmos DB mock

   - [ ] `CosmosDocumentMock` implementation
   - [ ] Factory function with document ID, partition key
   - [ ] Unit tests with >90% coverage

2. Advanced testing utilities

   - [ ] Custom pytest matchers (`assert_output_matches`)
   - [ ] Snapshot testing support
   - [ ] Pytest fixtures plugin

3. Examples
   - [ ] Real-world examples directory
   - [ ] Multi-trigger function example
   - [ ] Complex workflow example

**Success Criteria:**

- Beta release published to PyPI
- All examples documented and tested
- Comprehensive user guides complete

---

### Phase 5: Stable Release & Maintenance (Ongoing)

**Goal:** Gather feedback, stabilize API, release 1.0.0.

**Deliverables:**

1. Community feedback

   - [ ] Create GitHub Discussions
   - [ ] Respond to issues and PRs
   - [ ] Incorporate user feedback into API design

2. API stabilization

   - [ ] Review all public APIs for consistency
   - [ ] Add deprecation warnings if needed
   - [ ] Finalize type signatures

3. Stable release

   - [ ] Tag v1.0.0
   - [ ] Publish to PyPI (stable environment)
   - [ ] Announce on relevant communities

4. Maintenance
   - [ ] Set up Renovate for dependency updates
   - [ ] Monitor security advisories
   - [ ] Plan for future features (input bindings, more triggers)

**Success Criteria:**

- 1.0.0 released with stable API
- Active community engagement
- No critical bugs in issue tracker

---

## Quality Assurance

### Quality Gates

Every commit must pass these gates:

| Gate              | Tool               | Threshold                | Enforcement                |
| ----------------- | ------------------ | ------------------------ | -------------------------- |
| **Linting**       | Ruff               | Zero errors              | CI blocks on failure       |
| **Formatting**    | Ruff               | Consistent style         | CI blocks on failure       |
| **Type Coverage** | Pyright            | Strict mode, zero errors | CI blocks on failure       |
| **Test Coverage** | pytest-cov         | >90% line coverage       | CI warns below 90%         |
| **Security**      | Bandit + pip-audit | No high/critical         | CI blocks on high/critical |
| **Multi-version** | pytest matrix      | 3.11, 3.12, 3.13         | CI blocks on any failure   |

### Code Review Checklist

- [ ] All public APIs have docstrings with examples
- [ ] Type hints on all function signatures
- [ ] Tests added for new functionality
- [ ] No decrease in code coverage
- [ ] CHANGELOG.md updated (if user-facing change)
- [ ] Documentation updated (if API change)

### Testing Strategy

**Unit Tests:**

- Test each mock type in isolation
- Test `BaseMock` extension points
- Test `FunctionTestContext` output capture
- Mock Azure Functions SDK where necessary

**Integration Tests:**

- Test real Azure Functions code using our mocks
- Verify SDK compatibility
- Test end-to-end workflows

**Property-Based Tests (Future):**

- Use Hypothesis for edge case discovery
- Test invariants (e.g., serialization round-trips)

---

## Technology Stack

### Core Dependencies

| Package             | Version  | Purpose                             |
| ------------------- | -------- | ----------------------------------- |
| **Python**          | >=3.11   | Runtime (3.11, 3.12, 3.13)         |
| **azure-functions** | >=1.17.0 | SDK we're mocking (peer dependency) |

### Development Dependencies

| Package        | Version   | Purpose                           |
| -------------- | --------- | --------------------------------- |
| **pytest**     | >=8.0     | Test framework                    |
| **pytest-cov** | >=4.0     | Coverage reporting                |
| **pyright**    | >=1.1.350 | Static type checker (strict mode) |
| **ruff**       | >=0.3     | Linting + formatting              |
| **bandit**     | >=1.7     | Security vulnerability scanning   |
| **pip-audit**  | >=2.7     | Dependency vulnerability scanning |

### Documentation Dependencies

| Package                  | Version | Purpose                                |
| ------------------------ | ------- | -------------------------------------- |
| **mkdocs**               | >=1.5   | Documentation site generator           |
| **mkdocs-material**      | >=9.5   | Material theme for MkDocs              |
| **mkdocstrings[python]** | >=0.24  | Auto-generate API docs from docstrings |

### Tooling Stack

| Tool          | Purpose                                              | Configuration File |
| ------------- | ---------------------------------------------------- | ------------------ |
| **uv**        | Package manager, virtual env, build tool             | pyproject.toml     |
| **Ruff**      | Linting + formatting (replaces flake8, black, isort) | pyproject.toml     |
| **Pyright**   | Type checking (strict mode)                          | pyproject.toml     |
| **pytest**    | Test runner + fixtures                               | pyproject.toml     |
| **Hatch**     | Build backend with VCS versioning                    | pyproject.toml     |
| **git-cliff** | Changelog generation from commits                    | cliff.toml         |
| **Renovate**  | Automated dependency updates                         | renovate.json      |

---

## Success Metrics

### Technical Metrics

| Metric                  | Target                          | Current |
| ----------------------- | ------------------------------- | ------- |
| **Test Coverage**       | >90%                            | TBD     |
| **Type Coverage**       | 100% (strict)                   | TBD     |
| **Build Time**          | <30s                            | TBD     |
| **Test Execution Time** | <5s                             | TBD     |
| **PyPI Downloads**      | 1k/month (6 months post-launch) | 0       |

### Adoption Metrics

| Metric                       | Target (6 months) | Current |
| ---------------------------- | ----------------- | ------- |
| **GitHub Stars**             | 100+              | 0       |
| **Contributors**             | 5+                | 1       |
| **Open Issues**              | <10               | 0       |
| **Documentation Page Views** | 500+/month        | 0       |

### Quality Metrics

| Metric                   | Target          | Current |
| ------------------------ | --------------- | ------- |
| **Critical Bugs**        | 0               | 0       |
| **P1 Issues (< 7 days)** | 100% resolution | N/A     |
| **PR Review Time**       | <48 hours       | N/A     |

---

## Risk Assessment & Mitigation

### Technical Risks

| Risk                      | Impact | Likelihood | Mitigation                                       |
| ------------------------- | ------ | ---------- | ------------------------------------------------ |
| **Azure SDK API changes** | High   | Medium     | Pin SDK version ranges, monitor breaking changes |
| **Type incompatibility**  | Medium | Low        | Strict Pyright checks, SDK compatibility tests   |
| **Performance overhead**  | Low    | Low        | Lazy initialization, profile before optimizing   |

### Project Risks

| Risk                     | Impact | Likelihood | Mitigation                                                 |
| ------------------------ | ------ | ---------- | ---------------------------------------------------------- |
| **Low adoption**         | Medium | Medium     | Focus on docs, examples, community engagement              |
| **Maintenance burden**   | Medium | Medium     | Automate updates (Renovate), clear contribution guidelines |
| **Breaking SDK changes** | High   | Low        | Semantic versioning, deprecation warnings                  |

---

## Future Considerations

### Post-1.0 Features

- **Input Binding Mocks**: Mock Cosmos DB inputs, Blob inputs, etc.
- **Advanced Matchers**: Regex, JSON schema validation, custom predicates
- **Test Fixtures**: Pre-built common test data (users, orders, etc.)
- **Async Support**: Async function testing utilities
- **Durable Functions**: Mock orchestration/activity contexts
- **Snapshot Testing**: Compare outputs to saved snapshots

### Long-Term Vision

- **Official Azure Support**: Collaborate with Azure Functions team for official endorsement
- **Cross-Language Ports**: TypeScript/JavaScript, C#, Java versions
- **VS Code Extension**: Generate test boilerplate from function definitions

---

## Appendix

### Glossary

| Term                    | Definition                                                                  |
| ----------------------- | --------------------------------------------------------------------------- |
| **Mock**                | Test double that simulates behavior of real objects                         |
| **Factory Function**    | Function that creates and configures objects (e.g., `mock_queue_message()`) |
| **Output Binding**      | Azure Functions concept: data written by function (queue, blob, etc.)       |
| **Duck Typing**         | Type compatibility based on behavior, not inheritance                       |
| **Lazy Initialization** | Delaying object construction until first use                                |

### References

- [Azure Functions Python Developer Guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Document Version:** 1.0
**Author:** Sudarshan
**Last Review:** 2025-12-19
