#!/bin/bash

# Exit on error
set -e

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
echo "Installing development dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p docs/api
mkdir -p docs/examples
mkdir -p docs/tutorials

# Initialize git hooks
echo "Initializing git hooks..."
git config core.hooksPath .git/hooks/

# Set up VS Code settings (if VS Code is installed)
if command -v code >/dev/null 2>&1; then
    echo "Setting up VS Code..."
    code --install-extension ms-python.python
    code --install-extension ms-python.vscode-pylance
    code --install-extension ms-python.black-formatter
    code --install-extension ms-python.flake8
    code --install-extension ms-python.mypy-type-checker
    code --install-extension ms-python.isort
fi

echo "Development environment setup complete!"
echo "To activate the virtual environment, run: source venv/bin/activate"
