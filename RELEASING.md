# Release Process

This document describes how to create releases for `azure-functions-test`.

## Release Philosophy

Our release strategy:

- **Bug-fix releases**: Every few weeks for critical fixes
- **Minor releases**: Every 2-3 months for new features
- **Major releases**: When adding support for new `azure-functions` major versions

We aim to get fixes and features out quickly rather than holding them for large releases.

## Versioning Strategy

This package follows **version-compatible versioning** with the `azure-functions` library:

- `1.17.0` = Stable release compatible with `azure-functions 1.17.x`
- `1.17.1` = Bug-fix release (patch)
- `1.18.0` = New minor release (when `azure-functions 1.18.x` is released)
- `2.0.0` = Major release (breaking changes)

### Pre-releases

Pre-releases use PEP 440 format:

- `1.17.0a1` = Alpha release 1
- `1.17.0b1` = Beta release 1
- `1.17.0rc1` = Release candidate 1

## Prerequisites

### Git Remotes

Ensure you have the following remotes:

- `origin`: Your fork
- `upstream`: The official `sudzxd/azure-functions-test` repository

```bash
git remote -v
# origin    https://github.com/YOUR_USERNAME/azure-functions-test.git
# upstream  https://github.com/sudzxd/azure-functions-test.git
```

### Required Permissions

- Write access to the repository
- PyPI publishing permissions (configured via GitHub environments)

## Release Methods

We support two release methods:

1. **Manual Tag-Based Release** (recommended for maintainers)
2. **Workflow Dispatch** (for quick releases)

---

## Method 1: Manual Tag-Based Release (Recommended)

This is the standard process documented in CONTRIBUTING.md.

### Step 1: Create Release Branch

Branch from `develop`:

```bash
git checkout develop
git pull upstream develop
git checkout -b release/vX.Y.Z
```

Examples:
- Bug-fix: `release/v1.17.1`
- Minor: `release/v1.18.0`
- Pre-release: `release/v1.17.0a1`

### Step 2: Update CHANGELOG

Edit `CHANGELOG.md` to document the release:

```markdown
## [1.17.1] - 2025-12-XX

### Fixed
- Fix issue with HTTP form parsing (#123)
- Correct timer schedule status handling (#124)

### Added
- Support for additional blob metadata properties (#125)

[1.17.1]: https://github.com/sudzxd/azure-functions-test/releases/tag/v1.17.1
```

Commit the changes:

```bash
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for v1.17.1"
```

### Step 3: Rebase on Main

Rebase your release branch onto `main`:

```bash
git fetch upstream main
git rebase upstream/main
```

### Step 4: Push and Verify

Push the release branch:

```bash
git push upstream release/vX.Y.Z
```

Wait for CI to pass. All checks must be green:
- Tests on Python 3.11, 3.12, 3.13
- Linting (Ruff)
- Type checking (Pyright)
- Coverage checks

### Step 5: Merge to Main

Create a PR from `release/vX.Y.Z` → `main`:

```bash
gh pr create --base main --head release/vX.Y.Z \
  --title "Release vX.Y.Z" \
  --body "Release vX.Y.Z

See CHANGELOG.md for details."
```

**Important**: Merge using **merge commit** (not squash):

```bash
gh pr merge --merge
```

### Step 6: Tag the Release

After merging, tag the merge commit on `main`:

```bash
git checkout main
git pull upstream main
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push upstream vX.Y.Z
```

**Tagging triggers the automated release workflow** which will:

1. ✅ Run full test suite
2. ✅ Build package
3. ✅ Publish to PyPI
4. ✅ Create GitHub release with changelog

### Step 7: Verify Publication

Check that the release was successful:

- **PyPI**: https://pypi.org/project/azure-functions-test/
- **GitHub Releases**: https://github.com/sudzxd/azure-functions-test/releases

### Step 8: Merge Back to Develop

Cherry-pick the CHANGELOG update to `develop`:

```bash
git checkout develop
git pull upstream develop
git cherry-pick -m1 upstream/main
git push upstream develop
```

---

## Method 2: Workflow Dispatch (Quick Releases)

For urgent releases, you can trigger the release workflow manually without creating a tag first.

### Via GitHub UI

1. Go to [Actions → Release](https://github.com/sudzxd/azure-functions-test/actions/workflows/release.yml)
2. Click "Run workflow"
3. Enter the version (e.g., `v1.17.1`)
4. Click "Run workflow"

### Via GitHub CLI

```bash
gh workflow run release.yml \
  -f version=v1.17.1
```

**Note**: This method still requires the CHANGELOG to be updated beforehand and the release branch to be merged to `main`.

---

## Release Types

### Bug-Fix Releases (Patch: X.Y.Z → X.Y.Z+1)

For critical fixes:

1. Create `release/v1.17.1` from `develop`
2. Ensure CHANGELOG mentions all fixes
3. Follow standard process above

**When to release**:
- Critical bugs affecting users
- Security vulnerabilities
- Documentation errors

### Minor Releases (Minor: X.Y.Z → X.Y+1.0)

For new features:

1. Create `release/v1.18.0` from `develop`
2. Ensure CHANGELOG lists all new features
3. Follow standard process above

**When to release**:
- New trigger types added
- New major features
- Compatibility with new `azure-functions` minor version

### Major Releases (Major: X.Y.Z → X+1.0.0)

For breaking changes:

1. Create `release/v2.0.0` from `develop`
2. Clearly document breaking changes in CHANGELOG
3. Update migration guide (if needed)
4. Follow standard process above

**When to release**:
- Breaking API changes
- Dropping Python version support
- Major refactoring

### Pre-Releases (Alpha, Beta, RC)

For testing before stable release:

**Alpha** (`a1`, `a2`, ...):
```bash
git checkout -b release/v1.17.0a1
# Update CHANGELOG
git tag -a v1.17.0a1 -m "Release v1.17.0a1"
git push upstream v1.17.0a1
```

**Beta** (`b1`, `b2`, ...):
```bash
git tag -a v1.17.0b1 -m "Release v1.17.0b1"
git push upstream v1.17.0b1
```

**Release Candidate** (`rc1`, `rc2`, ...):
```bash
git tag -a v1.17.0rc1 -m "Release v1.17.0rc1"
git push upstream v1.17.0rc1
```

Pre-releases automatically use the `pypi-prerelease` environment, which may have different approval requirements.

---

## Post-Release Tasks

After a successful release:

### 1. Announcement

Send announcement email with content from CHANGELOG to:
- Project mailing list (if applicable)
- Community channels

Post on social media:
- Twitter/X with `#pytest` `#azure` `#python`
- LinkedIn
- Reddit (r/Python, r/azure)

### 2. Documentation

For minor/major releases:

- Ensure docs are deployed to GitHub Pages
- Update any external documentation
- Update examples if API changed

### 3. Close Milestone

If using GitHub milestones:

1. Go to [Milestones](https://github.com/sudzxd/azure-functions-test/milestones)
2. Close the milestone for this version
3. Create milestone for next version

---

## Troubleshooting

### Release Workflow Failed

If the automated release fails:

1. Check the [Actions tab](https://github.com/sudzxd/azure-functions-test/actions)
2. Review the failed job logs
3. Common issues:
   - **Tests failed**: Fix on release branch and re-tag
   - **PyPI publish failed**: Check PyPI credentials in GitHub secrets
   - **Build failed**: Verify `pyproject.toml` configuration

### Wrong Version Tagged

If you tagged the wrong version:

```bash
# Delete local tag
git tag -d vX.Y.Z

# Delete remote tag
git push upstream :refs/tags/vX.Y.Z
```

**Note**: If PyPI publish succeeded, you cannot re-upload the same version. Use a new patch version.

### Rollback a Release

You cannot delete a PyPI release. Instead:

1. Release a new patch version with fixes
2. Mark the bad release as "yanked" on PyPI (if critical)
3. Add notice in GitHub release notes

---

## Future Improvements

### Automated Prepare-Release Workflow

Similar to pytest, we could add a `prepare-release-pr` workflow that:

1. Automatically determines version based on changelog
2. Updates CHANGELOG with release date
3. Creates a PR with all changes

**Proposed inputs**:
- `branch`: Target maintenance branch (e.g., `1.17.x`)
- `major`: Whether this is a major release
- `prerelease`: Pre-release suffix (e.g., `rc1`)

**Versioning logic**:
- If `major=yes`: Bump major (e.g., `1.17.0` → `2.0.0`)
- If breaking changes in CHANGELOG: Bump minor (e.g., `1.17.0` → `1.18.0`)
- Otherwise: Bump patch (e.g., `1.17.0` → `1.17.1`)

### Maintenance Branches

For long-term support, create maintenance branches:

```bash
# Create 1.17.x maintenance branch
git checkout -b 1.17.x main
git push upstream 1.17.x
```

Bug-fixes can be backported to maintenance branches as needed.

---

## Questions?

- Open an issue for release process questions
- Tag `@sudzxd` for urgent release issues
- Check existing releases for examples
