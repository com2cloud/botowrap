"""Setup script for botowrap package."""

import os

from setuptools import find_packages, setup

# Read version from __init__.py
with open(os.path.join("botowrap", "__init__.py")) as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip("\"'")
            break

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="botowrap",
    version=version,
    author="Denys Melnyk",
    author_email="Com2Cloud@com2cloud.com",
    description="A modular framework for extending boto3 clients with enhancements and features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/com2cloud/botowrap",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.17.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "mypy>=0.800",
            "black>=22.3.0",
            "isort>=5.0.0",
            "ruff>=0.0.292",
            "moto>=2.0.0",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "twine>=3.4.0",
            "build>=0.7.0",
            "pre-commit>=3.0.0",
            "types-setuptools",
        ],
    },
    package_data={
        "botowrap": [
            "py.typed",
            "**/*.pyi",
            "docs/**/*",
            ".github/**/*",
            ".vscode/**/*",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
        "Framework :: Pytest",
        "Operating System :: OS Independent",
    ],
    keywords="boto3, aws, dynamodb, wrapper, extension, s3, lambda, sqs, aws-sdk, python, cloud",
)
