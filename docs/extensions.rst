Extensions
==========

Available Extensions
------------------

DynamoDB Extension
^^^^^^^^^^^^^^^^

The DynamoDB extension adds the following features to the boto3 DynamoDB client:

* **Automatic Serialization/Deserialization**: Convert between Python types and DynamoDB attribute values
* **Automatic Timestamps**: Add CreatedAt/UpdatedAt timestamps to items
* **Pagination Helpers**: Simplified pagination with scan_all and query_all methods
* **Throttling Retry**: Automatic retry with jittered exponential backoff
* **Capacity Logging**: Log consumed capacity for monitoring and optimization

Creating Custom Extensions
------------------------

You can create your own extensions by subclassing the BaseExtension class:

.. code-block:: python

    from typing import Dict, Any
    from boto3.session import Session as BotoSession
    from botowrap.core import BaseExtension

    class MyCustomExtension(BaseExtension):
        """Custom extension for XYZ service."""
        
        SERVICE = 'xyz'  # The AWS service name
        
        def __init__(self, config):
            self.config = config
            self._client_instances = []
        
        def attach(self, session: BotoSession) -> None:
            """Attach this extension to the session."""
            session.events.register(
                f'creating-client-class.{self.SERVICE}',
                self._attach_mixin,
                unique_id='xyz-bootstrap'
            )
        
        def detach(self, session: BotoSession) -> None:
            """Detach this extension from the session."""
            session.events.unregister(
                f'creating-client-class.{self.SERVICE}',
                unique_id='xyz-bootstrap'
            )
            # Clean up any instance handlers
            for client in self._client_instances:
                self._unregister_instance_handlers(client)
        
        def _attach_mixin(self, class_attrs: Dict[str, Any], base_classes: list, **_):
            """Add mixin to the client class."""
            base_classes.insert(0, MyCustomMixin)
        
        def _unregister_instance_handlers(self, client):
            """Clean up any handlers registered on the client."""
            # Unregister any instance-specific handlers

    class MyCustomMixin:
        """Mixin to add functionality to the client."""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add your functionality here
            
    # Then register and use your extension:
    from botowrap.core import ExtensionManager
    
    mgr = ExtensionManager()
    mgr.register(MyCustomExtension(config))
    mgr.bootstrap()