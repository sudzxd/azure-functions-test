# azure-functions-test

> Unit test Azure Functions without the runtime.

Fast, ergonomic, type-safe mock objects for testing Azure Functions. No runtime, no Azurite, no boilerplate.

[![PyPI version](https://img.shields.io/pypi/v/azure-functions-test.svg)](https://pypi.org/project/azure-functions-test/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-203%20passing-green.svg)](https://github.com/sudzxd/azure-functions-test)
[![Coverage](https://img.shields.io/badge/coverage-79.56%25-brightgreen.svg)](https://github.com/sudzxd/azure-functions-test)
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

## Documentation

📚 **[Full Documentation](https://sudzxd.github.io/azure-functions-test/)** - Complete documentation site

- [Getting Started Guide](https://sudzxd.github.io/azure-functions-test/getting-started/)
- [API Reference](https://sudzxd.github.io/azure-functions-test/api/)
- [Examples](./examples/) - Working code examples for all triggers
- [Contributing Guide](./CONTRIBUTING.md) - Development workflow and coding standards
- [Release Process](./RELEASING.md) - For maintainers

---

## Versioning

This package follows **version-compatible versioning** with the `azure-functions` library.

See [CHANGELOG.md](./CHANGELOG.md) for version history and compatibility details.

**Requirements:**
- Python: `3.11+`
- Azure Functions: `>=1.17.0`
- Pydantic: `>=2.0`

---

## Why This Library?

| Current Approach | Problem |
|-----------------|---------|
| **`func start` + Azurite** | Slow (5-10s startup), flaky, requires Docker |
| **Manual mocking** | Tedious boilerplate, inconsistent across projects |
| **Integration tests only** | Slow feedback loop, hard to test edge cases |
| **No testing** | Bugs in production |

**This library fills the gap:** Fast, ergonomic mocks with output capture and zero runtime dependency.

---

## Contributing

Contributions welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) for development setup and coding standards.

Please note that this project is released with a [Code of Conduct](./CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

**Quick start:**

```bash
git clone https://github.com/sudzxd/azure-functions-test
cd azure-functions-test
uv sync --all-extras
PYTHONPATH=src uv run pytest
```

**Run checks:**
```bash
uv run ruff check .              # Linting
PYTHONPATH=src uv run pyright    # Type checking
PYTHONPATH=src uv run pytest     # Tests with coverage
```

---

## Status

See [CHANGELOG.md](./CHANGELOG.md) for release history.

- 203 tests passing
- 79.56% code coverage
- Pyright strict mode: 0 errors
- All 6 core trigger types fully implemented

---

## License

Distributed under the MIT License. See [LICENSE](./LICENSE) for more information.

---

## Support

- **Documentation**: [sudzxd.github.io/azure-functions-test](https://sudzxd.github.io/azure-functions-test/)
- **Issues & Bug Reports**: [GitHub Issues](https://github.com/sudzxd/azure-functions-test/issues)

---

**Author:** Sudarshan
**Repository:** [github.com/sudzxd/azure-functions-test](https://github.com/sudzxd/azure-functions-test)
**PyPI:** [pypi.org/project/azure-functions-test](https://pypi.org/project/azure-functions-test/)

---

**⭐ Star this repo to follow progress!**
