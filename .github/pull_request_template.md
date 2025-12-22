## Summary

<!-- Provide a brief description of what this PR does and why -->

## Changes

<!-- List the main changes made in this PR -->

-
-
-

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Test coverage improvement
- [ ] CI/CD improvement

## Testing

<!-- Describe how you tested your changes -->

### Test Coverage

- [ ] Added new tests for new functionality
- [ ] Updated existing tests for modified functionality
- [ ] All tests pass locally (`PYTHONPATH=src uv run pytest`)
- [ ] Coverage maintained or improved

### Manual Testing

<!-- Describe any manual testing performed -->

```python
# Example of how you tested this
from azure_functions_test import mock_queue_message

# Test scenario...
```

## Quality Checks

<!-- All must pass before merging -->

- [ ] Code follows project style guidelines (`uv run ruff check .`)
- [ ] Code is properly formatted (`uv run ruff format --check .`)
- [ ] Type checking passes (`PYTHONPATH=src uv run pyright`)
- [ ] All tests pass (`PYTHONPATH=src uv run pytest`)
- [ ] Documentation updated (README, docstrings, API docs)
- [ ] CHANGELOG.md updated (if applicable)

## Compatibility

<!-- Check which azure-functions versions this is compatible with -->

- [ ] Compatible with azure-functions >=1.17.0
- [ ] Tested with Python 3.11
- [ ] Tested with Python 3.12
- [ ] Tested with Python 3.13

## Related Issues

<!-- Link related issues using "Closes #123" or "Fixes #456" -->

Closes #

## Screenshots / Examples

<!-- If applicable, add screenshots or usage examples -->

## Checklist

<!-- Final checklist before requesting review -->

- [ ] Branch is up to date with `develop`
- [ ] No merge conflicts
- [ ] CI checks pass
- [ ] Self-review completed
- [ ] Code is well-commented
- [ ] Changes are focused and minimal
- [ ] Ready for review

## Additional Notes

<!-- Any additional context, concerns, or notes for reviewers -->
