"""Tests for botowrap core functionality."""

import pytest
import boto3
from boto3.session import Session as BotoSession

from botowrap.core import BaseExtension, ExtensionManager


class MockExtension(BaseExtension):
    """Mock extension for testing."""

    def __init__(self):
        self.attached = False
        self.detached = False
        self.session = None

    def attach(self, session: BotoSession) -> None:
        """Mark the extension as attached."""
        self.attached = True
        self.session = session

    def detach(self, session: BotoSession) -> None:
        """Mark the extension as detached."""
        self.detached = True
        self.session = session


class TestBaseExtension:
    """Tests for the BaseExtension class."""

    def test_base_extension_methods(self):
        """Test that BaseExtension requires implementation of attach and detach."""
        ext = BaseExtension()
        session = boto3.Session()
        
        with pytest.raises(NotImplementedError):
            ext.attach(session)
            
        with pytest.raises(NotImplementedError):
            ext.detach(session)


class TestExtensionManager:
    """Tests for the ExtensionManager class."""

    def test_init_default_session(self):
        """Test that ExtensionManager initializes with default session if none provided."""
        mgr = ExtensionManager()
        assert mgr.session is not None
        assert isinstance(mgr.session, BotoSession)
        assert len(mgr._extensions) == 0

    def test_init_with_session(self):
        """Test that ExtensionManager initializes with provided session."""
        session = boto3.Session()
        mgr = ExtensionManager(session=session)
        assert mgr.session is session
        
    def test_register(self):
        """Test registering an extension."""
        mgr = ExtensionManager()
        ext = MockExtension()
        mgr.register(ext)
        assert len(mgr._extensions) == 1
        assert mgr._extensions[0] is ext
        
    def test_bootstrap(self):
        """Test bootstrapping attaches all registered extensions."""
        mgr = ExtensionManager()
        ext1 = MockExtension()
        ext2 = MockExtension()
        mgr.register(ext1)
        mgr.register(ext2)
        
        mgr.bootstrap()
        
        assert ext1.attached
        assert ext2.attached
        assert ext1.session is mgr.session
        assert ext2.session is mgr.session
        
    def test_teardown(self):
        """Test tearing down detaches all registered extensions."""
        mgr = ExtensionManager()
        ext1 = MockExtension()
        ext2 = MockExtension()
        mgr.register(ext1)
        mgr.register(ext2)
        
        mgr.bootstrap()
        mgr.teardown()
        
        assert ext1.detached
        assert ext2.detached
        assert ext1.session is mgr.session
        assert ext2.session is mgr.session