"""DynamoDB extension for botowrap.

Provides enhanced DynamoDB client functionality with automatic serialization/deserialization,
timestamp management, pagination helpers, and retry logic.
"""

import logging
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from boto3.session import Session as BotoSession
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from botowrap.core import BaseExtension

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

T = TypeVar("T")


@dataclass(frozen=True)
class DynamoDBConfig:
    """Configuration options for the DynamoDB extension."""

    max_retries: int = 5
    log_consumed: bool = True
    add_pagination: bool = True
    add_timestamps: bool = True


class DynamoDBExtension(BaseExtension):
    """Attaches all DynamoDB "document client" behavior onto boto3.client('dynamodb')."""

    SERVICE = "dynamodb"

    def __init__(self, config: DynamoDBConfig) -> None:
        """Initialize DynamoDB extension with the given configuration.

        Args:
        ----
            config: Configuration options for the DynamoDB extension

        """
        self.config = config
        self._client_instances: List[BaseClient] = []

    def attach(self, session: BotoSession) -> None:
        """Attach the DynamoDB extension to the given session.

        Registers event handlers to add document client functionality to DynamoDB clients
        created from this session.

        Args:
        ----
            session: The boto3 session to attach to

        """
        session.events.register(
            f"creating-client-class.{self.SERVICE}",
            self._attach_mixin,
            unique_id="dynamodb-doc-bootstrap",
        )

    def detach(self, session: BotoSession) -> None:
        """Detach the DynamoDB extension from the given session.

        Args:
        ----
            session: The boto3 session to detach from

        """
        session.events.unregister(
            f"creating-client-class.{self.SERVICE}", unique_id="dynamodb-doc-bootstrap"
        )
        # also unregister any instance-specific handlers
        for client in self._client_instances:
            self._unregister_instance_handlers(client)

    def _attach_mixin(self, **kwargs: Any) -> None:
        """Attach DocumentClientBootstrapper to the DynamoDB client class.

        This method is called when a DynamoDB client class is being created.
        It inserts the _DocumentClientBootstrapper class at the beginning
        of the client's base classes.

        Args:
        ----
            **kwargs: Keyword arguments from the creating-client-class event

        """
        # when the class is constructed, _DocumentClientBootstrapper will run __init__,
        # which in turn registers all the handlers on the new client instance
        base_classes = kwargs.get("base_classes", [])
        base_classes.insert(0, _DocumentClientBootstrapper)

    def _unregister_instance_handlers(self, client: BaseClient) -> None:
        """Unregister all handlers for a specific client instance.

        Args:
        ----
            client: The client instance to unregister handlers from

        """
        ev = client.meta.events
        ev.unregister("creating-client-class.dynamodb", unique_id="dynamodb-pagination")
        ev.unregister("provide-client-params.dynamodb.*", unique_id="dynamodb-inject-ts")
        ev.unregister("provide-client-params.dynamodb.*", unique_id="dynamodb-serialize")
        ev.unregister("after-call.dynamodb.GetItem", unique_id="dynamodb-deserialize-get")
        ev.unregister("after-call.dynamodb.Query", unique_id="dynamodb-deserialize-query")
        ev.unregister("after-call.dynamodb.Scan", unique_id="dynamodb-deserialize-scan")
        ev.unregister("after-call.dynamodb.BatchGetItem", unique_id="dynamodb-deserialize-batch")
        ev.unregister("needs-retry.dynamodb.*", unique_id="dynamodb-retry")
        ev.unregister("after-call.dynamodb.*", unique_id="dynamodb-log-cap")


class _DocumentClientBootstrapper:
    """Mixin that wires up all handlers on a new client instance."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the bootstrapper and attach document client functionality.

        Args:
        ----
            *args: Positional arguments to pass to parent initializer
            **kwargs: Keyword arguments to pass to parent initializer

        """
        super().__init__(*args, **kwargs)
        # Cast self to BaseClient since this mixin is intended to be used with BaseClient
        self._config = DynamoDBConfig()  # Add default config
        DynamoDBDocumentClient(cast("BaseClient", self))

    def _get_config(self) -> DynamoDBConfig:
        """Get the DynamoDB configuration.

        Returns
        -------
            The DynamoDB configuration

        """
        return self._config

    def _retry_throttling(
        self,
        response: Dict[str, Any],
        endpoint: Any,
        operation: Any,
        attempts: int,
        caught_exception: Optional[ClientError],
        request_dict: Dict[str, Any],
        **_: Any,
    ) -> bool:
        """Handle throttling retries for DynamoDB operations.

        Args:
        ----
            response: Response from the service
            endpoint: Endpoint used for the request
            operation: Operation being performed
            attempts: Number of attempts made so far
            caught_exception: Exception that was caught, if any
            request_dict: Request parameters
            **_: Additional keyword arguments

        Returns:
        -------
            bool: True if the operation should be retried, False otherwise

        """
        if (
            caught_exception is not None
            and hasattr(caught_exception, "response")
            and caught_exception.response.get("Error", {}).get("Code")
            == "ProvisionedThroughputExceededException"
            and attempts < self._get_config().max_retries
        ):
            time.sleep(random.uniform(0.05, 0.1) * (2**attempts))
            return True
        return False


def _wrap_retry_handler(handler: Callable[..., bool]) -> Callable[..., None]:
    """Wrap a retry handler to satisfy type checking while preserving behavior.

    Args:
    ----
        handler: The original handler that returns a bool

    Returns:
    -------
        A wrapped handler that satisfies the event system's type hints

    """

    def wrapped(*args: Any, **kwargs: Any) -> None:
        handler(*args, **kwargs)

    return wrapped


class DynamoDBDocumentClient:
    """DynamoDB document client wrapper.

    This class wraps a botocore DynamoDB client to provide document-style operations.
    It handles serialization and deserialization of Python types to/from DynamoDB's
    AttributeValue format, adds pagination helpers, automatic retries for throttling,
    and optional features like timestamp injection and capacity logging.

    The wrapper is automatically attached to new DynamoDB client instances via the
    _DocumentClientBootstrapper mixin.

    Attributes
    ----------
        client: The underlying botocore DynamoDB client
        serializer: TypeSerializer for converting Python types to DynamoDB format
        deserializer: TypeDeserializer for converting DynamoDB format to Python types
        config: Configuration options for the DynamoDB extension

    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize DynamoDB document client wrapper.

        Args:
        ----
            client: The DynamoDB client to wrap

        """
        self.client = client
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()
        self.config = getattr(
            client, "_config", DynamoDBConfig()
        )  # Get config from client or use default
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register event handlers for DynamoDB document client functionality."""
        ev = self.client.meta.events

        # Add pagination helpers
        if self.config.add_pagination:
            ev.register(
                "creating-client-class.dynamodb",
                self._add_pagination_helpers,
                unique_id="dynamodb-pagination",
            )

        # Add timestamp injection
        if self.config.add_timestamps:
            ev.register(
                "provide-client-params.dynamodb.*",
                self._inject_timestamps,
                unique_id="dynamodb-inject-ts",
            )

        # Add serialization
        ev.register(
            "provide-client-params.dynamodb.*",
            self._serialize_params,
            unique_id="dynamodb-serialize",
        )

        # Add deserialization for different operations
        ev.register(
            "after-call.dynamodb.GetItem",
            self._deserialize_item,
            unique_id="dynamodb-deserialize-get",
        )
        ev.register(
            "after-call.dynamodb.Query",
            self._deserialize_multi,
            unique_id="dynamodb-deserialize-query",
        )
        ev.register(
            "after-call.dynamodb.Scan",
            self._deserialize_multi,
            unique_id="dynamodb-deserialize-scan",
        )
        ev.register(
            "after-call.dynamodb.BatchGetItem",
            self._deserialize_batch,
            unique_id="dynamodb-deserialize-batch",
        )

        # Add retry handler for throttling
        ev.register(
            "needs-retry.dynamodb.*",
            _wrap_retry_handler(self._retry_throttling),
            unique_id="dynamodb-retry",
        )

        # Add capacity logging
        if self.config.log_consumed:
            ev.register(
                "after-call.dynamodb.*",
                self._log_capacity,
                unique_id="dynamodb-log-cap",
            )

    def _add_pagination_helpers(self, class_attrs: Dict[str, Any], **_: Any) -> None:
        """Add pagination helper methods to the DynamoDB client class.

        Adds query_all and scan_all methods that automatically handle pagination
        by collecting all items from multiple requests.

        Args:
        ----
            class_attrs: Dictionary of class attributes to modify
            **_: Additional keyword arguments (ignored)

        """

        def query_all(self: Any, **kw: Any) -> Dict[str, List[Dict[str, Any]]]:
            """Execute a Query operation, automatically handling pagination.

            Args:
            ----
                self: The DynamoDB client instance
                **kw: Keyword arguments to pass to the query method

            Returns:
            -------
                Dict with Items key containing all results

            """
            items = []
            resp = self.query(**kw)
            items.extend(resp.get("Items", []))
            while "LastEvaluatedKey" in resp:
                resp = self.query(**kw, ExclusiveStartKey=resp["LastEvaluatedKey"])
                items.extend(resp.get("Items", []))
            return {"Items": items}

        def scan_all(self: Any, **kw: Any) -> Dict[str, List[Dict[str, Any]]]:
            """Execute a Scan operation, automatically handling pagination.

            Args:
            ----
                self: The DynamoDB client instance
                **kw: Keyword arguments to pass to the scan method

            Returns:
            -------
                Dict with Items key containing all results

            """
            items = []
            resp = self.scan(**kw)
            items.extend(resp.get("Items", []))
            while "LastEvaluatedKey" in resp:
                resp = self.scan(**kw, ExclusiveStartKey=resp["LastEvaluatedKey"])
                items.extend(resp.get("Items", []))
            return {"Items": items}

        class_attrs["query_all"] = query_all
        class_attrs["scan_all"] = scan_all

    def _inject_timestamps(
        self, params: Dict[str, Any], operation_name: Optional[str] = None, **_: Any
    ) -> None:
        """Inject CreatedAt and UpdatedAt timestamps into items.

        Args:
        ----
            params: The parameters for the DynamoDB operation
            operation_name: The name of the operation being performed
            **_: Additional keyword arguments (ignored)

        """
        if operation_name in ("PutItem", "UpdateItem"):
            item = params.get("Item", {})
            now = int(time.time())
            if operation_name == "PutItem":
                item["CreatedAt"] = now
            item["UpdatedAt"] = now

    def _serialize_params(self, params: Dict[str, Any], **_: Any) -> None:
        """Serialize Python types to DynamoDB AttributeValue format.

        Args:
        ----
            params: The parameters for the DynamoDB operation
            **_: Additional keyword arguments (ignored)

        """

        def to_attr(v: Any) -> Dict[str, Any]:
            """Convert a Python value to a DynamoDB AttributeValue.

            Args:
            ----
                v: The Python value to convert

            Returns:
            -------
                A DynamoDB AttributeValue dictionary

            """
            # Use cast to tell mypy that the return value is a Dict[str, Any]
            return cast("Dict[str, Any]", self.serializer.serialize(v))

        if "Item" in params:
            params["Item"] = {k: to_attr(v) for k, v in params["Item"].items()}
        if "Expected" in params:
            for _k, v in params["Expected"].items():
                if "Value" in v:
                    v["Value"] = to_attr(v["Value"])
        if "ExpressionAttributeValues" in params:
            params["ExpressionAttributeValues"] = {
                k: to_attr(v) for k, v in params["ExpressionAttributeValues"].items()
            }

    def _deserialize_item(self, http: Any, parsed: Dict[str, Any], **_: Any) -> None:
        """Deserialize a single item from DynamoDB format.

        Args:
        ----
            http: The HTTP response
            parsed: The parsed response data
            **_: Additional keyword arguments (ignored)

        """
        if "Item" in parsed:
            parsed["Item"] = {
                k: self.deserializer.deserialize(v) for k, v in parsed["Item"].items()
            }

    def _deserialize_multi(self, http: Any, parsed: Dict[str, Any], **_: Any) -> None:
        """Deserialize multiple items from DynamoDB format.

        Args:
        ----
            http: The HTTP response
            parsed: The parsed response data
            **_: Additional keyword arguments (ignored)

        """
        if "Items" in parsed:
            parsed["Items"] = [
                {k: self.deserializer.deserialize(v) for k, v in item.items()}
                for item in parsed["Items"]
            ]

    def _deserialize_batch(self, http: Any, parsed: Dict[str, Any], **_: Any) -> None:
        """Deserialize items from a batch operation.

        Args:
        ----
            http: The HTTP response
            parsed: The parsed response data
            **_: Additional keyword arguments (ignored)

        """
        for _table_name, table_data in parsed.get("Responses", {}).items():
            if "Items" in table_data:
                table_data["Items"] = [
                    {k: self.deserializer.deserialize(v) for k, v in item.items()}
                    for item in table_data["Items"]
                ]

    def _retry_throttling(
        self,
        response: Dict[str, Any],
        endpoint: Any,
        operation: Any,
        attempts: int,
        caught_exception: Optional[ClientError],
        request_dict: Dict[str, Any],
        **_: Any,
    ) -> bool:
        """Handle throttling retries for DynamoDB operations.

        Args:
        ----
            response: Response from the service
            endpoint: Endpoint used for the request
            operation: Operation being performed
            attempts: Number of attempts made so far
            caught_exception: Exception that was caught, if any
            request_dict: Request parameters
            **_: Additional keyword arguments

        Returns:
        -------
            bool: True if the operation should be retried, False otherwise

        """
        if (
            caught_exception is not None
            and hasattr(caught_exception, "response")
            and caught_exception.response.get("Error", {}).get("Code")
            == "ProvisionedThroughputExceededException"
            and attempts < self.config.max_retries
        ):
            time.sleep(random.uniform(0.05, 0.1) * (2**attempts))
            return True
        return False

    def _log_capacity(self, parsed: Dict[str, Any], model: Any, http: Any = None, **_: Any) -> None:
        """Log consumed capacity information from DynamoDB responses.

        Args:
        ----
            parsed: Parsed response data
            model: Operation model
            http: HTTP response object (optional)
            **_: Additional keyword arguments

        """
        if not self.config.log_consumed:
            return

        if "ConsumedCapacity" not in parsed:
            return

        capacity = parsed["ConsumedCapacity"]
        if isinstance(capacity, list):
            for table_capacity in capacity:
                logger.info(
                    "DynamoDB consumed capacity for table %s: %s",
                    table_capacity.get("TableName", "Unknown"),
                    table_capacity.get("CapacityUnits", 0),
                )
        else:
            logger.info(
                "DynamoDB consumed capacity for table %s: %s",
                capacity.get("TableName", "Unknown"),
                capacity.get("CapacityUnits", 0),
            )
