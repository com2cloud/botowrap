import logging
import random
import time
from dataclasses import dataclass
from typing import Any, Dict

import boto3
import botocore
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from boto3.session import Session as BotoSession
from botocore.exceptions import ClientError

from botowrap.core import BaseExtension

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@dataclass(frozen=True)
class DynamoDBConfig:
    max_retries: int = 5
    log_consumed: bool = True
    add_pagination: bool = True
    add_timestamps: bool = True


class DynamoDBExtension(BaseExtension):
    """
    Attaches all DynamoDB “document client” behavior onto boto3.client('dynamodb').
    """

    SERVICE = "dynamodb"

    def __init__(self, config: DynamoDBConfig):
        self.config = config
        self._client_instances = []

    def attach(self, session: BotoSession) -> None:
        session.events.register(
            f"creating-client-class.{self.SERVICE}",
            self._attach_mixin,
            unique_id="dynamodb-doc-bootstrap",
        )

    def detach(self, session: BotoSession) -> None:
        session.events.unregister(
            f"creating-client-class.{self.SERVICE}", unique_id="dynamodb-doc-bootstrap"
        )
        # also unregister any instance‐specific handlers
        for client in self._client_instances:
            self._unregister_instance_handlers(client)

    def _attach_mixin(self, **kwargs):
        # when the class is constructed, _DocumentClientBootstrapper will run __init__,
        # which in turn registers all the handlers on the new client instance
        class_attrs = kwargs.get('class_attributes', {})
        base_classes = kwargs.get('base_classes', [])
        base_classes.insert(0, _DocumentClientBootstrapper)


class _DocumentClientBootstrapper:
    """Mixin that wires up all handlers on a new client instance."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        DynamoDBDocumentClient(self)


class DynamoDBDocumentClient:
    def __init__(self, client: botocore.client.BaseClient):
        self.client = client
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()
        cfg = self._get_config()
        self.max_retries = cfg.max_retries
        self.log_consumed = cfg.log_consumed
        self.add_pagination = cfg.add_pagination
        self.add_timestamps = cfg.add_timestamps
        self._register_handlers()

    def _get_config(self) -> DynamoDBConfig:
        # retrieve the same config object stored on the Extension
        # via boto3.DEFAULT_SESSION; simplistic lookup for demo:
        for ext in boto3.DEFAULT_SESSION._user_agent_extra.split():
            pass
        # In real code, you'd pass config via closure or a weakmap.
        return DynamoDBConfig()

    def _register_handlers(self):
        ev = self.client.meta.events

        if self.add_pagination:
            ev.register(
                "creating-client-class.dynamodb",
                self._add_pagination_helpers,
                unique_id="dynamodb-pagination",
            )

        if self.add_timestamps:
            ev.register(
                "provide-client-params.dynamodb.*",
                self._inject_timestamps,
                unique_id="dynamodb-inject-ts",
            )

        ev.register(
            "provide-client-params.dynamodb.*",
            self._serialize_params,
            unique_id="dynamodb-serialize",
        )
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
        ev.register("needs-retry.dynamodb.*", self._retry_throttling, unique_id="dynamodb-retry")
        if self.log_consumed:
            ev.register("after-call.dynamodb.*", self._log_capacity, unique_id="dynamodb-log-cap")

    def _add_pagination_helpers(self, class_attrs, **_):
        def query_all(self, **kw):
            items = []
            resp = self.query(**kw)
            items.extend(resp.get("Items", []))
            while "LastEvaluatedKey" in resp:
                resp = self.query(**kw, ExclusiveStartKey=resp["LastEvaluatedKey"])
                items.extend(resp.get("Items", []))
            return {"Items": items}

        def scan_all(self, **kw):
            items = []
            resp = self.scan(**kw)
            items.extend(resp.get("Items", []))
            while "LastEvaluatedKey" in resp:
                resp = self.scan(**kw, ExclusiveStartKey=resp["LastEvaluatedKey"])
                items.extend(resp.get("Items", []))
            return {"Items": items}

        class_attrs["query_all"] = query_all
        class_attrs["scan_all"] = scan_all

    def _inject_timestamps(self, params, operation_name=None, **_):
        ts = int(time.time())
        if operation_name == "PutItem":
            itm = params.setdefault("Item", {})
            itm.setdefault("CreatedAt", ts)
            itm["UpdatedAt"] = ts
        elif operation_name == "UpdateItem":
            expr = params.get("UpdateExpression", "")
            sep = " " if expr and not expr.endswith(" ") else ""
            params["UpdateExpression"] = f"{expr}{sep}SET UpdatedAt = :u"
            params.setdefault("ExpressionAttributeValues", {})[":u"] = ts
        return params

    def _serialize_params(self, params, **_):
        def to_attr(v):
            return self.serializer.serialize(v)

        for key in ("Item", "Key"):
            if key in params and isinstance(params[key], dict):
                params[key] = {k: to_attr(v) for k, v in params[key].items()}
        return params

    def _deserialize_item(self, http, parsed, **_):
        itm = parsed.get("Item", {})
        parsed["Item"] = {k: self.deserializer.deserialize(v) for k, v in itm.items()}
        return parsed

    def _deserialize_multi(self, http, parsed, **_):
        lst = parsed.get("Items", [])
        parsed["Items"] = [
            {k: self.deserializer.deserialize(v) for k, v in itm.items()} for itm in lst
        ]
        return parsed

    def _deserialize_batch(self, http, parsed, **_):
        out = {}
        for tbl, lst in parsed.get("Responses", {}).items():
            out[tbl] = [
                {k: self.deserializer.deserialize(v) for k, v in itm.items()} for itm in lst
            ]
        parsed["Responses"] = out
        return parsed

    def _retry_throttling(
        self, response, endpoint, operation, attempts, caught_exception, request_dict, **_
    ):
        if attempts >= self.max_retries:
            return None
        if isinstance(caught_exception, ClientError):
            code = caught_exception.response["Error"]["Code"]
            throttle_exceptions = ("ProvisionedThroughputExceededException", "ThrottlingException")
            if code in throttle_exceptions:
                backoff = min(0.5 * (2**attempts), 10.0)
                delay = backoff + random.random() * 0.1
                logger.debug(f"retrying {operation.name} in {delay:.2f}s")
                return delay
        return None

    def _log_capacity(self, http, parsed, model, **_):
        cap = parsed.get("ConsumedCapacity")
        if cap:
            logger.info(f"DynamoDB {model.name} ConsumedCapacity: {cap}")
        return parsed

    def _unregister_instance_handlers(self, client):
        ev = client.meta.events
        for uid in (
            "dynamodb-pagination",
            "dynamodb-inject-ts",
            "dynamodb-serialize",
            "dynamodb-deserialize-get",
            "dynamodb-deserialize-query",
            "dynamodb-deserialize-scan",
            "dynamodb-deserialize-batch",
            "dynamodb-retry",
            "dynamodb-log-cap",
        ):
            ev.unregister(event_name=None, unique_id=uid)
