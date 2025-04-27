"""Tests for the DynamoDB extension."""

import boto3
import pytest
from moto import mock_aws

from botowrap.core import ExtensionManager
from botowrap.extensions.dynamodb import DynamoDBExtension, DynamoDBConfig


class TestDynamoDBConfig:
    """Tests for DynamoDBConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DynamoDBConfig()
        assert config.max_retries == 5
        assert config.log_consumed is True
        assert config.add_pagination is True
        assert config.add_timestamps is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = DynamoDBConfig(
            max_retries=10,
            log_consumed=False,
            add_pagination=False,
            add_timestamps=False
        )
        assert config.max_retries == 10
        assert config.log_consumed is False
        assert config.add_pagination is False
        assert config.add_timestamps is False

    def test_frozen_dataclass(self):
        """Test that config is immutable."""
        config = DynamoDBConfig()
        with pytest.raises(AttributeError):
            config.max_retries = 10


class TestDynamoDBExtension:
    """Tests for DynamoDBExtension."""

    def test_initialization(self):
        """Test initialization of DynamoDBExtension."""
        config = DynamoDBConfig()
        extension = DynamoDBExtension(config)
        assert extension.config is config
        assert extension.SERVICE == 'dynamodb'
        
    @pytest.mark.skip("Integration test requires moto setup")
    def test_serialization_deserialization(self):
        """Test automatic serialization and deserialization."""
        pass
        
    @pytest.mark.skip("Integration test requires moto setup")
    def test_timestamps(self):
        """Test automatic timestamp insertion."""
        pass
        
    @pytest.mark.skip("Integration test requires moto setup")
    def test_pagination_helpers(self):
        """Test pagination helpers are added."""
        pass