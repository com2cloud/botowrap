Installation
============

Requirements
-----------

Botowrap requires:

* Python 3.7 or higher
* boto3 1.17.0 or higher

Installing from PyPI
------------------

The recommended way to install botowrap is from PyPI:

.. code-block:: bash

    pip install botowrap

This will install the latest stable version of botowrap and its dependencies.

Installing for Development
------------------------

If you want to contribute to botowrap, install it in development mode:

.. code-block:: bash

    git clone https://github.com/com2cloud/botowrap.git
    cd botowrap
    pip install -e ".[dev]"

This will install the package in development mode along with all the development dependencies.

Verifying Installation
--------------------

You can verify your installation by running:

.. code-block:: python

    import botowrap
    print(botowrap.__version__)

This should print the version of botowrap you have installed.
