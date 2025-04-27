# Deployment Guide

This document explains how to release a new version of botowrap to PyPI.

## Release Process

The project uses GitHub Actions to automate the release process. When you're ready to release a new version, follow these steps:

1. **Update the version number** in `botowrap/__init__.py`:
   ```python
   __version__ = "0.2.0"  # Update to the new version
   ```

2. **Update the CHANGELOG.md** with details of the changes:
   ```markdown
   ## [0.2.0] - YYYY-MM-DD

   ### Added
   - New feature 1
   - New feature 2

   ### Changed
   - Improvement 1
   - Improvement 2

   ### Fixed
   - Bug fix 1
   - Bug fix 2
   ```

3. **Commit and push these changes** to the repository:
   ```bash
   git add botowrap/__init__.py CHANGELOG.md
   git commit -m "Prepare release v0.2.0"
   git push origin main
   ```

4. **Create and push a new tag** matching the version number:
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

## What Happens Next?

When you push the tag, GitHub Actions will automatically:

1. Run all tests, linting, and type checking to ensure the package is ready
2. Build the package (sdist and wheel)
3. Create a GitHub Release with notes from the CHANGELOG
4. Publish the package to PyPI

## Testing the Release Process

If you want to test the release process without publishing to the main PyPI repository, you can:

1. Go to your GitHub repository and navigate to the "Actions" tab
2. Select "Test PyPI Publish" from the workflows list
3. Click "Run workflow" and confirm

This will build and publish your package to TestPyPI. You can then install it with:

```bash
pip install --index-url https://test.pypi.org/simple/ botowrap
```

## Setting Up Credentials

For the GitHub Actions to publish to PyPI, you need to set up authentication:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add two repository secrets:
   - `PYPI_USERNAME`: Your PyPI username
   - `PYPI_PASSWORD`: Your PyPI API token (preferred) or password

To publish to TestPyPI, you'll need to set up additional secrets:
   - `TEST_PYPI_USERNAME`: Your TestPyPI username
   - `TEST_PYPI_PASSWORD`: Your TestPyPI API token

## API Tokens vs. Passwords

It's recommended to use API tokens instead of your PyPI password:

1. Go to https://pypi.org/manage/account/
2. Click on "API tokens" → "Add API token"
3. Create a token with the "Upload to PyPI" scope
4. Use this token as the `PYPI_PASSWORD` secret

Follow the same process on TestPyPI (https://test.pypi.org) for the `TEST_PYPI_PASSWORD` secret.
