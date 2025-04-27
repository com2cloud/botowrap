# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documentation setup with Sphinx
- Type hints with py.typed marker
- Unit and integration tests
- CI/CD pipeline with GitHub Actions

## [0.1.0] - Initial Release

### Added
- Core ExtensionManager to manage boto3 extensions
- BaseExtension abstract class for creating extensions
- DynamoDBExtension with document client features:
  - Python↔DynamoDB (de)serialization
  - Auto-CreatedAt/UpdatedAt timestamps
  - Jittered exponential backoff on throttling
  - query_all/scan_all pagination helpers
  - ConsumedCapacity logging
