Contributing
============

We welcome contributions to botowrap! This page provides guidelines for contributing to the project.

Development Setup
---------------

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/com2cloud/botowrap.git
       cd botowrap

2. Install development dependencies:

   .. code-block:: bash

       pip install -e ".[dev]"

3. Set up pre-commit hooks:

   .. code-block:: bash

       pre-commit install

Code Style
---------

We follow these conventions:

* PEP 8 for code style
* Type annotations for all public functions and methods
* Docstrings for all classes and functions
* Maximum line length of 100 characters

Testing
------

All code should be tested. We use pytest for testing:

.. code-block:: bash

    pytest

For coverage reports:

.. code-block:: bash

    pytest --cov=botowrap tests/

Pull Request Process
------------------

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests to ensure they pass
5. Run the type checker and linter:

   .. code-block:: bash

       mypy botowrap
       flake8 botowrap tests

6. Update documentation if necessary
7. Submit a pull request

Creating New Extensions
---------------------

When creating a new extension:

1. Create a new file in ``botowrap/extensions/``
2. Inherit from ``BaseExtension``
3. Implement the required ``attach`` and ``detach`` methods
4. Add appropriate tests in ``tests/``
5. Update the documentation to include your new extension

Versioning
---------

We use semantic versioning (MAJOR.MINOR.PATCH):

* MAJOR version for incompatible API changes
* MINOR version for backwards-compatible functionality
* PATCH version for backwards-compatible bug fixes

Release Process
-------------

To create a new release:

1. Update version in ``botowrap/__init__.py``
2. Update ``CHANGELOG.md``
3. Create a new tag with the version number
4. Push to GitHub
5. The CI/CD pipeline will automatically build and publish to PyPI
