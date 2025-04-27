"""Basic example showing how to use the DynamoDB extension.

This example demonstrates core functionality of the botowrap DynamoDB extension:
- Automatic serialization/deserialization
- Automatic timestamp insertion
- Pagination helpers
"""

import logging
import time

import boto3

from botowrap.core import ExtensionManager
from botowrap.extensions.dynamodb import DynamoDBConfig, DynamoDBExtension

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create and configure the extension manager
mgr = ExtensionManager()
ddb_config = DynamoDBConfig(
    max_retries=3, log_consumed=True, add_pagination=True, add_timestamps=True
)
mgr.register(DynamoDBExtension(ddb_config))
mgr.bootstrap()

# Create table (assuming local DynamoDB)
ddb = boto3.client("dynamodb", endpoint_url="http://localhost:8000")

# Check if table exists, create if not
try:
    ddb.describe_table(TableName="ExampleUsers")
    print("Table already exists")
except ddb.exceptions.ResourceNotFoundException:
    print("Creating ExampleUsers table...")
    ddb.create_table(
        TableName="ExampleUsers",
        KeySchema=[{"AttributeName": "UserId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "UserId", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    print("Waiting for table creation...")
    ddb.get_waiter("table_exists").wait(TableName="ExampleUsers")
    print("Table created")

# Insert items - notice we use Python native types
users = [
    {"UserId": "user1", "Name": "Alice", "Age": 30, "Active": True},
    {"UserId": "user2", "Name": "Bob", "Age": 25, "Active": False},
    {"UserId": "user3", "Name": "Charlie", "Age": 35, "Active": True},
]

for user in users:
    ddb.put_item(TableName="ExampleUsers", Item=user)
    print(f"Added user: {user['Name']}")

# Small delay to ensure consistent read
time.sleep(1)

# Get a single item - notice the response is automatically deserialized
response = ddb.get_item(TableName="ExampleUsers", Key={"UserId": "user1"})
print(f"Single user: {response['Item']}")
print(
    f"Notice the timestamps: "
    f"{response['Item'].get('CreatedAt')}, {response['Item'].get('UpdatedAt')}"
)

# Use the pagination helper
all_users = ddb.scan_all(TableName="ExampleUsers")
print(f"All users (scan_all): {all_users['Items']}")

# Update an item
ddb.update_item(
    TableName="ExampleUsers",
    Key={"UserId": "user2"},
    UpdateExpression="SET Age = :a, Active = :s",
    ExpressionAttributeValues={":a": 26, ":s": True},
)

# Verify update
response = ddb.get_item(TableName="ExampleUsers", Key={"UserId": "user2"})
print(f"Updated user: {response['Item']}")
print(f"Notice UpdatedAt changed: {response['Item'].get('UpdatedAt')}")
