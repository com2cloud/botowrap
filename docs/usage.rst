Usage
=====

Basic Usage
----------

Here's a basic example of how to use botowrap:

.. code-block:: python

    import logging
    import boto3
    from botowrap.core import ExtensionManager
    from botowrap.extensions.dynamodb import DynamoDBExtension, DynamoDBConfig

    # Set up logging to see the enhancements in action
    logging.basicConfig(level=logging.INFO)

    # 1) Create an extension manager (uses the default boto3 session)
    mgr = ExtensionManager()

    # 2) Configure and register the DynamoDB extension
    ddb_config = DynamoDBConfig(
        max_retries=5,
        log_consumed=True,
        add_pagination=True,
        add_timestamps=True
    )
    mgr.register(DynamoDBExtension(ddb_config))

    # 3) Bootstrap the extensions (this enhances boto3 clients)
    mgr.bootstrap()

    # Now any DynamoDB client you create will have all the enhancements
    ddb = boto3.client('dynamodb')

    # Use native Python types - automatic serialization
    ddb.put_item(
        TableName='Users',
        Item={
            'UserId': 'alice',
            'Age': 30,
            'Active': True,
            'Metadata': {'LastLogin': '2023-01-01'}
        }
    )

    # Get item returns deserialized Python types
    user = ddb.get_item(
        TableName='Users',
        Key={'UserId': 'alice'}
    )
    print(user['Item'])  # Python dict with native types

    # Use pagination helpers
    all_users = ddb.scan_all(TableName='Users')
    print(all_users['Items'])  # All items in one response

Extension Configuration
---------------------

Each extension in botowrap can be configured to suit your specific needs. For example, the DynamoDB extension
can be configured with these options:

.. code-block:: python

    ddb_config = DynamoDBConfig(
        # Number of retries for throttling exceptions
        max_retries=5,

        # Whether to log DynamoDB consumed capacity
        log_consumed=True,

        # Add pagination helpers (scan_all, query_all)
        add_pagination=True,

        # Add automatic CreatedAt/UpdatedAt timestamps
        add_timestamps=True
    )

Advanced Usage
------------

Using Multiple Extensions
^^^^^^^^^^^^^^^^^^^^^^^

You can register multiple extensions with the same manager:

.. code-block:: python

    from botowrap.core import ExtensionManager
    from botowrap.extensions.dynamodb import DynamoDBExtension, DynamoDBConfig

    # Create manager
    mgr = ExtensionManager()

    # Register DynamoDB extension
    mgr.register(DynamoDBExtension(DynamoDBConfig()))

    # Register other extensions as they become available
    # mgr.register(OtherExtension(OtherConfig()))

    # Bootstrap all extensions
    mgr.bootstrap()

Using a Custom Session
^^^^^^^^^^^^^^^^^^^

If you need to use a specific boto3 session:

.. code-block:: python

    import boto3
    from botowrap.core import ExtensionManager

    # Create a custom session
    session = boto3.Session(
        region_name='us-west-2',
        profile_name='development'
    )

    # Create manager with the custom session
    mgr = ExtensionManager(session=session)

    # Register and bootstrap extensions as normal
    # ...

    # Now create clients using your session
    ddb = session.client('dynamodb')  # Enhanced client
