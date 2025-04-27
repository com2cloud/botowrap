"""Botowrap extensions package.

This package contains various extensions for boto3 clients, including
enhanced DynamoDB functionality.
"""

from .dynamodb import DynamoDBConfig, DynamoDBExtension

__all__ = [
    "DynamoDBConfig",
    "DynamoDBExtension",
]
