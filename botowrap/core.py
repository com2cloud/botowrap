from typing import List

import boto3
from boto3.session import Session as BotoSession


class BaseExtension:
    """
    Base class for all client-extension wrappers.
    Subclasses must implement attach(session) and detach(session).
    """

    def attach(self, session: BotoSession) -> None:
        raise NotImplementedError

    def detach(self, session: BotoSession) -> None:
        raise NotImplementedError


class ExtensionManager:
    """
    Holds and bootstraps a collection of BaseExtension instances.
    """

    def __init__(self, session: BotoSession = None):
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
