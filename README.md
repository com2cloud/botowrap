# botowrap

[![Python Package](https://github.com/com2cloud/botowrap/actions/workflows/python-package.yml/badge.svg)](https://github.com/com2cloud/botowrap/actions/workflows/python-package.yml)
[![PyPI version](https://badge.fury.io/py/botowrap.svg)](https://badge.fury.io/py/botowrap)
[![PyPI downloads](https://img.shields.io/pypi/dm/botowrap.svg)](https://pypi.org/project/botowrap/)
[![Codecov](https://codecov.io/gh/com2cloud/botowrap/branch/main/graph/badge.svg)](https://codecov.io/gh/com2cloud/botowrap)
[![Documentation Status](https://readthedocs.org/projects/botowrap/badge/?version=latest)](https://botowrap.readthedocs.io/en/latest/?badge=latest)
[![CodeFactor](https://www.codefactor.io/repository/github/com2cloud/botowrap/badge)](https://www.codefactor.io/repository/github/com2cloud/botowrap)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A modular framework for building and distributing "opinionated" wrappers around
boto3 clients. Enhance your AWS SDK experience with powerful extensions that add
developer-friendly features while maintaining the standard boto3 interface.

Out of the box it provides:

- **DynamoDBDocumentExtension**
  - Python↔DynamoDB (de)serialization
  - Auto‐`CreatedAt`/`UpdatedAt` timestamps
  - Jittered exponential backoff on throttling
  - `query_all`/`scan_all` pagination helpers
  - ConsumedCapacity logging

## Installation

```bash
pip install botowrap
```

## Usage

```python
import logging
import boto3
from botowrap.core import ExtensionManager
from botowrap.extensions.dynamodb import (
    DynamoDBExtension, DynamoDBConfig
)

logging.basicConfig(level=logging.INFO)

# 1) Create the manager (uses the default boto3 session)
mgr = ExtensionManager()

# 2) Register whichever extensions you want:
ddb_config = DynamoDBConfig(
    max_retries=8,
    log_consumed=True,
    add_pagination=True,
    add_timestamps=True
)
mgr.register(DynamoDBExtension(ddb_config))

# 3) Bootstrap: from now on, boto3.client('dynamodb') is enhanced
mgr.bootstrap()

# Use the enhanced client
ddb = boto3.client('dynamodb')

# Insert item with native Python types (automatic serialization)
ddb.put_item(
    TableName='Users',
    Item={
        'UserId': 'alice',
        'Age': 30,
        'Active': True,
        'Data': {'joined': '2023-01-01'}
    }
)

# Use pagination helper
all_users = ddb.scan_all(TableName='Users')
print(all_users)  # All users with Python types
```

## Features

### Automatic Type Conversion

No more manual serialization between Python and DynamoDB types:

```python
# Without botowrap
from boto3.dynamodb.types import TypeSerializer
serializer = TypeSerializer()
ddb.put_item(
    TableName='Users',
    Item={
        'UserId': serializer.serialize('alice'),
        'Age': serializer.serialize(30),
        'Active': serializer.serialize(True)
    }
)

# With botowrap
ddb.put_item(
    TableName='Users',
    Item={
        'UserId': 'alice',
        'Age': 30,
        'Active': True
    }
)
```

### Automatic Timestamps

Keep track of when items were created and last modified:

```python
# Creates an item with CreatedAt and UpdatedAt timestamps
ddb.put_item(TableName='Users', Item={'UserId': 'bob'})

# UpdatedAt is automatically updated, CreatedAt preserved
ddb.update_item(
    TableName='Users',
    Key={'UserId': 'bob'},
    UpdateExpression='SET Age = :a',
    ExpressionAttributeValues={':a': 25}
)
```

### Simplified Pagination

No more dealing with LastEvaluatedKey tokens manually:

```python
# With botowrap
all_items = ddb.scan_all(TableName='MyTable')

# Equivalent to:
items = []
resp = ddb.scan(TableName='MyTable')
items.extend(resp.get('Items', []))
while 'LastEvaluatedKey' in resp:
    resp = ddb.scan(
        TableName='MyTable',
        ExclusiveStartKey=resp['LastEvaluatedKey']
    )
    items.extend(resp.get('Items', []))
```

## Configuration Options

The DynamoDB extension can be configured:

```python
ddb_config = DynamoDBConfig(
    # Number of retries for throttling (default: 5)
    max_retries=8,

    # Whether to log consumed capacity (default: True)
    log_consumed=True,

    # Whether to add pagination helpers (default: True)
    add_pagination=True,

    # Whether to add CreatedAt/UpdatedAt timestamps (default: True)
    add_timestamps=True
)
```

## Developing

* New service wrappers live under `botowrap/extensions/`
* Base classes and manager logic are in `core.py`
* Extensions must implement:
  * `attach(session)` - Adds functionality to the boto3 session
  * `detach(session)` - Removes functionality from the boto3 session

### Creating an Extension

```python
from botowrap.core import BaseExtension

class MyServiceExtension(BaseExtension):
    SERVICE = 'my-service'

    def __init__(self, config):
        self.config = config

    def attach(self, session):
        # Add functionality to the session
        pass

    def detach(self, session):
        # Remove functionality from the session
        pass
```

## Documentation

For full documentation, visit the [documentation site](https://botowrap.readthedocs.io/).

## Contributing

Contributions are welcome! See the [CONTRIBUTING](CONTRIBUTING.md) guide for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
