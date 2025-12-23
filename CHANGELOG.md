# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.17.0a1] - 2025-12-23

### Added
- Initial alpha release
- Queue Storage trigger mock with Pydantic validation
- HTTP Request mock with form data support
- Timer trigger mock with schedule tracking
- Blob Storage mock with stream support
- Service Bus mock with sessions, dead-letter, and correlation tracking
- Event Grid mock with custom and Azure system events
- FunctionTestContext for output binding capture
- Full Pyright strict mode compliance (0 errors)
- Comprehensive test suite (203 tests passing)
- Complete API documentation
- GitHub Actions CI/CD workflows
- MkDocs documentation site

### Features
- 6 trigger types fully supported
- Zero runtime dependency (no Azure Functions runtime required)
- Type-safe with Protocol-based duck typing
- SDK-compatible drop-in replacements
- 75.94% code coverage

[Unreleased]: https://github.com/sudzxd/azure-functions-test/compare/v1.17.0a1...HEAD
[1.17.0a1]: https://github.com/sudzxd/azure-functions-test/releases/tag/v1.17.0a1
