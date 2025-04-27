"""Core functionality for botowrap extensions.

Provides base classes and managers for extending boto3 clients.
"""

from typing import List, Optional

import boto3
from boto3.session import Session as BotoSession


class BaseExtension:
    """Base class for all client-extension wrappers.

    Subclasses must implement attach(session) and detach(session).
    """

    def attach(self, session: BotoSession) -> None:
        """Attach this extension to the given boto3 session."""
        raise NotImplementedError

    def detach(self, session: BotoSession) -> None:
        """Detach this extension from the given boto3 session."""
        raise NotImplementedError


class ExtensionManager:
    """Holds and bootstraps a collection of BaseExtension instances."""

    def __init__(self, session: Optional[BotoSession] = None):
        """Initialize with an optional boto3 session."""
        self.session = session or boto3.DEFAULT_SESSION or BotoSession()
        self._extensions: List[BaseExtension] = []

    def register(self, ext: BaseExtension) -> None:
        """Add an extension to be bootstrapped."""
        self._extensions.append(ext)

    def bootstrap(self) -> None:
        """Attach all registered extensions to the session."""
        for ext in self._extensions:
            ext.attach(self.session)

    def teardown(self) -> None:
        """Detach all registered extensions (e.g. for tests)."""
        for ext in self._extensions:
            ext.detach(self.session)
