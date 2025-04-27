"""Type stubs for DynamoDB extension."""

from dataclasses import dataclass
from typing import Any

import botocore
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from boto3.session import Session as BotoSession

from botowrap.core import BaseExtension

@dataclass(frozen=True)
class DynamoDBConfig:
    max_retries: int = 5
    log_consumed: bool = True
    add_pagination: bool = True
    add_timestamps: bool = True

class DynamoDBExtension(BaseExtension):
    """Attaches all DynamoDB "document client" behavior onto boto3.client('dynamodb')."""

    SERVICE: str
    config: DynamoDBConfig
    _client_instances: list[Any]

    def __init__(self, config: DynamoDBConfig) -> None: ...
    def attach(self, session: BotoSession) -> None: ...
    def detach(self, session: BotoSession) -> None: ...
    def _attach_mixin(self, **kwargs: Any) -> None: ...
    def _unregister_instance_handlers(self, client: Any) -> None: ...

class _DocumentClientBootstrapper:
    """Mixin that wires up all handlers on a new client instance."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class DynamoDBDocumentClient:
    client: botocore.client.BaseClient
    serializer: TypeSerializer
    deserializer: TypeDeserializer
    max_retries: int
    log_consumed: bool
    add_pagination: bool
    add_timestamps: bool

    def __init__(self, client: botocore.client.BaseClient) -> None: ...
    def _get_config(self) -> DynamoDBConfig: ...
    def _register_handlers(self) -> None: ...
    def _add_pagination_helpers(self, class_attrs: dict[str, Any], **_: Any) -> None: ...
    def _inject_timestamps(
        self, params: dict[str, Any], operation_name: str | None = None, **_: Any
    ) -> dict[str, Any]: ...
    def _serialize_params(self, params: dict[str, Any], **_: Any) -> dict[str, Any]: ...
    def _deserialize_item(self, http: Any, parsed: dict[str, Any], **_: Any) -> dict[str, Any]: ...
    def _deserialize_multi(self, http: Any, parsed: dict[str, Any], **_: Any) -> dict[str, Any]: ...
    def _deserialize_batch(self, http: Any, parsed: dict[str, Any], **_: Any) -> dict[str, Any]: ...
    def _retry_throttling(
        self,
        response: Any,
        endpoint: Any,
        operation: Any,
        attempts: int,
        caught_exception: Any,
        request_dict: Any,
        **_: Any,
    ) -> float | None: ...
    def _log_capacity(
        self, http: Any, parsed: dict[str, Any], model: Any, **_: Any
    ) -> dict[str, Any]: ...
