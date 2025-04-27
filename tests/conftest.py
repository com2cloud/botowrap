"""Test configuration and fixtures."""

import boto3
import pytest
from moto import mock_aws

from botowrap.core import ExtensionManager
from botowrap.extensions.dynamodb import DynamoDBExtension, DynamoDBConfig


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    boto3.setup_default_session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        aws_session_token="testing",
        region_name="us-east-1",
    )


@pytest.fixture
def mock_all_aws_services(aws_credentials):
    """Mock all AWS services."""
    with mock_aws():
        yield


@pytest.fixture
def dynamodb_resource(mock_all_aws_services):
    """Get a DynamoDB resource with moto."""
    return boto3.resource("dynamodb")


@pytest.fixture
def dynamodb_table(dynamodb_resource):
    """Create a mock DynamoDB table for testing."""
    table = dynamodb_resource.create_table(
        TableName="TestTable",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    return table


@pytest.fixture
def extension_manager():
    """Create a fresh extension manager."""
    session = boto3.DEFAULT_SESSION or boto3.Session()
    return ExtensionManager(session=session)


@pytest.fixture
def dynamodb_extension():
    """Create a DynamoDB extension with default config."""
    return DynamoDBExtension(DynamoDBConfig())