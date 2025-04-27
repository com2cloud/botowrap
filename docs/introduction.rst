Introduction
============

What is botowrap?
----------------

Botowrap is a modular framework for extending boto3 clients with automatic enhancements, wrappers, and developer-friendly features. It provides a structured way to add functionality to the standard boto3 clients.

Key Features
-----------

* **Modular Extension System**: Easily add or remove features from boto3 clients
* **Type-Safe**: Full type annotations for better IDE integration
* **DynamoDB Enhancement**: Includes a powerful DynamoDB document client with:
   * Python↔DynamoDB (de)serialization
   * Auto‐CreatedAt/UpdatedAt timestamps
   * Jittered exponential backoff on throttling
   * query_all/scan_all pagination helpers
   * ConsumedCapacity logging

Design Philosophy
---------------

Botowrap is designed to be:

1. **Non-intrusive**: It enhances boto3 clients without changing their core behavior
2. **Modular**: Extensions can be added or removed independently
3. **Transparent**: The enhanced clients behave just like standard boto3 clients, but with extra features
4. **Typed**: Full type annotations provide excellent IDE integration and type safety

Use Cases
--------

* Simplifying DynamoDB interaction by automatically handling serialization/deserialization
* Adding automatic timestamps for data auditing
* Implementing consistent retry logic across your application
* Standardizing logging and monitoring of AWS resource usage
