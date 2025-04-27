# Contributing to botowrap

Thank you for considering contributing to botowrap! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/botowrap.git
   cd botowrap
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Environment

We recommend using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Development Workflow

1. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and add tests for new functionality

3. Run the linters and tests:
   ```bash
   # Run type checking
   mypy botowrap

   # Run style checks
   flake8 botowrap tests
   black --check botowrap tests
   isort --check botowrap tests

   # Run tests
   pytest
   ```

4. Submit a pull request

## Pull Request Process

1. Ensure all tests pass and code meets style guidelines
2. Update the documentation, including docstrings
3. Update the README.md if needed
4. Update CHANGELOG.md with your changes under the "Unreleased" section
5. The project maintainers will review your pull request

## Coding Guidelines

- Follow PEP 8 style guidelines
- Add type annotations to all functions and methods
- Write docstrings for all public functions, classes, and methods
- Keep lines to a maximum of 100 characters
- Use clear variable and function names
- Add unit tests for new functionality

## Creating a New Extension

When creating a new extension:

1. Create a new file in `botowrap/extensions/` 
2. Implement the `BaseExtension` interface
3. Write comprehensive tests
4. Update documentation

Example structure for a new extension:

```python
from dataclasses import dataclass
from typing import Any, Dict, List

from boto3.session import Session as BotoSession
from botowrap.core import BaseExtension


@dataclass(frozen=True)
class MyServiceConfig:
    # Configuration fields with defaults
    option1: bool = True
    option2: int = 5


class MyServiceExtension(BaseExtension):
    """
    Extension for the my-service client.
    
    Detailed description of what this extension does...
    """
    SERVICE = 'my-service'
    
    def __init__(self, config: MyServiceConfig):
        self.config = config
        self._client_instances = []
        
    def attach(self, session: BotoSession) -> None:
        """Attach this extension to the session."""
        # Implementation...
        
    def detach(self, session: BotoSession) -> None:
        """Detach this extension from the session."""
        # Implementation...
```

## Testing

All code should have tests:

- Unit tests: Test individual components in isolation
- Integration tests: Test with actual AWS services using moto

When submitting a PR, make sure your code is well-tested:
```bash
pytest --cov=botowrap tests/
```

## Documentation

Update the documentation when making changes:

- Add docstrings for all public classes and methods
- Update the Sphinx documentation in `docs/`
- Add examples showing how to use new features

To build the documentation locally:
```bash
cd docs
make html
```

## Versioning

We use [Semantic Versioning](https://semver.org/):

- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backwards-compatible manner
- PATCH version for backwards-compatible bug fixes

## Releasing

Project maintainers can release new versions:

1. Update version in `botowrap/__init__.py`
2. Update CHANGELOG.md
3. Create a git tag for the version
4. Push to GitHub
5. CI/CD will handle the PyPI release

## Questions?

If you have questions about contributing, please open an issue on GitHub.