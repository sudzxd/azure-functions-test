# Contributing to azure-functions-test

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branching Strategy](#branching-strategy)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Quality Standards](#code-quality-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions. We're here to build great software together.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/sudzxd/azure-functions-test.git
cd azure-functions-test

# Install dependencies
uv sync --all-extras

# Verify setup
PYTHONPATH=src uv run pytest
PYTHONPATH=src uv run pyright
uv run ruff check .
```

## Development Workflow

1. **Find or Create an Issue**

   - Check existing issues first
   - Create a new issue if needed
   - Get consensus on the approach before significant work

2. **Create a Branch**

   - Always branch from `develop`
   - Follow naming convention: `{type}/{initials}/{issue-number}-{description}`
   - Types: `feature`, `fix`, `docs`, `refactor`, `test`

3. **Make Changes**

   - Write code following our style guide
   - Add/update tests
   - Update documentation
   - Run quality checks locally

4. **Submit Pull Request**

   - Target `develop` branch (not `main`)
   - Fill out the PR template completely
   - Link related issues
   - Wait for CI checks to pass

5. **Code Review**

   - Address review feedback
   - Keep discussions constructive
   - Update PR as needed

6. **Merge**
   - Maintainers will merge once approved
   - PRs go to `develop` first
   - Periodic merge candidates from `develop` to `main`

## Branching Strategy

### Branch Structure

```bash
main (production)
  └── develop (integration)
       ├── feature/ss/10-contributing-guidelines
       ├── fix/ss/5-configure-uv-system-python
       └── docs/ss/8-version-compatible-strategy
```

### Branch Types

- **`main`** - Production-ready code, releases only

  - Protected branch
  - Merges only via merge commits from `develop`
  - Never commit directly

- **`develop`** - Integration branch

  - Protected branch
  - All feature branches merge here first
  - Staging area for next release

- **`feature/{initials}/{issue-number}-{description}`** - New features
- **`fix/{initials}/{issue-number}-{description}`** - Bug fixes
- **`docs/{initials}/{issue-number}-{description}`** - Documentation updates
- **`refactor/{initials}/{issue-number}-{description}`** - Code refactoring
- **`test/{initials}/{issue-number}-{description}`** - Test improvements

### Branch Naming Examples

```bash
feature/ss/15-add-cosmos-db-mock
fix/ss/23-http-request-form-parsing
docs/ss/10-contributing-guidelines
refactor/ss/18-simplify-context-api
test/ss/20-improve-coverage
```

## Commit Guidelines

### Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates
- `ci`: CI/CD changes

### Commit Examples

```bash
feat(mocks): add Cosmos DB trigger mock

Implements mock_cosmos_db_trigger() factory function with full
property support and document change tracking.

Closes #15

---

fix(http): correct form data parsing for multipart requests

The form data parser was not handling multipart/form-data correctly
when files were included. Updated to use proper boundary detection.

Fixes #23

---

docs: add contributing guidelines and templates

- Add CONTRIBUTING.md with development workflow
- Create issue templates for bugs and features
- Add PR template with checklist
- Document branching and merging strategy

Closes #10
```

## Pull Request Process

### Before Submitting

- [ ] Create an issue first (unless it's a trivial change)
- [ ] Branch from `develop`
- [ ] Follow branch naming convention
- [ ] Write clear, focused commits
- [ ] Add/update tests for changes
- [ ] Update documentation
- [ ] Run all quality checks locally

### Quality Checks

```bash
# Run all checks (must pass before PR)
uv run ruff format --check .         # Formatting
uv run ruff check .                  # Linting
PYTHONPATH=src uv run pyright        # Type checking
PYTHONPATH=src uv run pytest         # Tests
```

### PR Title Format

Use conventional commit format:

```bash
feat: add Cosmos DB mock support
fix: correct HTTP form parsing
docs: update installation instructions
```

### PR Description Template

The PR template will guide you, but include:

1. **Summary** - What and why
2. **Changes** - Bullet points of changes
3. **Testing** - How you tested
4. **Related Issues** - Link issues with `Closes #123`
5. **Screenshots** - If UI/docs changes

### Review Process

- All PRs require 1 approving review
- All CI checks must pass
- Address feedback constructively
- Keep PR scope focused

### Merging Strategy

- **To `develop`**: Use squash or merge commits (your choice)
- **To `main`**: **Only merge commits** (preserves history)
- Maintainers will handle merges to `main` via release branches (see Release Process below)

## Code Quality Standards

### Style Guide

- Follow PEP 8 (enforced by Ruff)
- Maximum line length: 88 characters
- Use type hints for all functions
- Write docstrings for public APIs

### Type Safety

- Full Pyright strict mode compliance
- No `Any` types without justification
- Use Protocol types for duck typing

### Testing

- Write tests for all new features
- Maintain >75% code coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### Documentation

- Update README.md for user-facing changes
- Add docstrings with examples
- Update API documentation
- Include inline comments for complex logic

## Testing

### Running Tests

```bash
# All tests
PYTHONPATH=src uv run pytest

# With coverage
PYTHONPATH=src uv run pytest --cov

# Specific test file
PYTHONPATH=src uv run pytest tests/test_http.py

# Specific test function
PYTHONPATH=src uv run pytest tests/test_http.py::test_form_data_parsing
```

### Writing Tests

```python
def test_feature_description():
    """Test that feature works correctly."""
    # Arrange
    mock = mock_queue_message({"data": "value"})

    # Act
    result = mock.get_json()

    # Assert
    assert result["data"] == "value"
```

### Test Organization

- `tests/` - All test files
- `tests/test_*.py` - Test modules
- Follow same structure as `src/`

## Documentation

### What to Document

- Public APIs (docstrings with examples)
- README.md (user-facing features)
- API docs in `docs/api/`
- Inline comments (complex logic only)

### Documentation Style

```python
def mock_cosmos_db_trigger(
    documents: list[dict[str, Any]],
    *,
    collection_name: str = "Items",
    database_name: str = "Database",
) -> MockCosmosDBTrigger:
    """Create a mock Cosmos DB trigger for testing.

    Args:
        documents: List of document dictionaries that triggered the function
        collection_name: Name of the Cosmos DB collection (default: "Items")
        database_name: Name of the Cosmos DB database (default: "Database")

    Returns:
        Mock Cosmos DB trigger object compatible with azure-functions

    Example:
        >>> trigger = mock_cosmos_db_trigger([
        ...     {"id": "1", "name": "Alice"},
        ...     {"id": "2", "name": "Bob"},
        ... ])
        >>> assert len(trigger) == 2
        >>> assert trigger[0]["name"] == "Alice"
    """
```

## Release Process

Maintainers handle releases, but here's the process:

1. **Create Release Branch**: Branch from `develop` with name `release/vX.Y.Z`
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.17.0
   ```

2. **Rebase Main**: Rebase `main` onto the release branch
   ```bash
   git fetch origin main
   git rebase origin/main
   ```

3. **Push and Verify**: Push release branch and let CI build and verify
   ```bash
   git push origin release/v1.17.0
   ```
   - All tests must pass
   - All quality checks must pass
   - Build verification succeeds

4. **Merge to Main**: Create PR from release branch to `main` (merge commit only)
   - Review final changes
   - Ensure CI is green
   - Merge using merge commit (not squash)

5. **Tag Release**: Create version tag on `main`
   ```bash
   git checkout main
   git pull origin main
   git tag -a v1.17.0 -m "Release v1.17.0"
   git push origin v1.17.0
   ```

6. **Automatic Publishing**: GitHub Actions will automatically:
   - Run full test suite
   - Build package
   - Publish to PyPI
   - Create GitHub release with changelog

## Questions?

- Open an issue for questions
- Tag maintainers if urgent
- Check existing issues/PRs first

Thank you for contributing! 🚀
