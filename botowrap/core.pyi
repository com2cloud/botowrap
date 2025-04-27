"""Type stubs for botowrap core module."""

from typing import List, Optional

from boto3.session import Session as BotoSession

class BaseExtension:
    """
    Base class for all client‐extension wrappers.
    Subclasses must implement attach(session) and detach(session).
    """

    def attach(self, session: BotoSession) -> None: ...
    def detach(self, session: BotoSession) -> None: ...

class ExtensionManager:
    """
    Holds and bootstraps a collection of BaseExtension instances.
    """

    session: BotoSession
    _extensions: List[BaseExtension]

    def __init__(self, session: Optional[BotoSession] = None) -> None: ...
    def register(self, ext: BaseExtension) -> None: ...
    def bootstrap(self) -> None: ...
    def teardown(self) -> None: ...
