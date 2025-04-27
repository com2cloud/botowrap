"""
Botowrap - A modular framework for extending boto3 clients with enhancements.

This package provides a way to add functionality to boto3 clients through
extensions that attach to boto3 sessions. Currently supports enhanced DynamoDB
client functionality.
"""

__version__ = "0.1.0"

from .core import BaseExtension, ExtensionManager
from .extensions.dynamodb import DynamoDBConfig, DynamoDBExtension

__all__ = [
    "BaseExtension",
    "ExtensionManager",
    "DynamoDBExtension",
    "DynamoDBConfig",
]
