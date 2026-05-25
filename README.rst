.. contents::

Guillotina_audit: ElasticSearch Logging for Audit Trail in Guillotina Framework
===============================================================================

Aim of the package?
-------------------

The main purpose of this package is to enable auditing and monitoring
of changes made to Guillotina objects. By integrating Elasticsearch as
the logging backend, it allows for efficient indexing and searching of
the audit logs.

When an object is created, modified, or deleted within the Guillotina
system, the `guillotina_audit` package captures relevant information
about the event, such as the object ID, the timestamp of the action,
the type of action (create, update, delete), and any additional
relevant data.

This information is then sent to Elasticsearch, which stores it in a
structured format. Elasticsearch provides powerful search
capabilities, allowing you to query and analyze the audit logs based
on various criteria, such as object ID, timestamps, action types, and
more.

By logging changes and events in Elasticsearch, `guillotina_audit`
facilitates monitoring and tracking of object activities in the
Guillotina system. It helps in ensuring data integrity, tracking user
actions, investigating issues, and maintaining a historical record of
object modifications.

The package provides an essential auditing layer for transparency and
accountability, helping users gain insights into the changes happening
within the Guillotina system and enabling effective monitoring and
analysis of object-level activities.

Installation
------------

``pip install guillotina-audit`` installs the Elasticsearch 9.x Python client.


Compatibility
-------------

``guillotina_audit`` 3.x requires Python 3.10 or newer and Guillotina 7.0.0
or newer. It uses ``elasticsearch[async]>=9.0.0,<10.0.0`` and supports
Elasticsearch clusters 7.x, 8.x and 9.x through Elasticsearch compatibility
headers.


Configuration
-------------

config.yaml can include elasticsearch section. Add this to your
guillotina config file

.. code-block:: yaml

    audit:
      index_name: "audit"
      connection_settings:
        hosts:
          - "http://127.0.0.1:9200"
        sniffer_timeout: 0.5
        sniff_on_start: true



Installation on a site
----------------------

Guillotina_audit comes as an addon for guillotina. To install it in your site:

"POST", "/db/guillotina/@addons", data=json.dumps({"id": "audit"})


Uninstall on a site
-------------------

"DELETE", "/db/guillotina/@addons", data=json.dumps({"id": "audit"})

Uninstalling will not delete the log entries created in ES.


Development and testing
-----------------------

Setup your python virtual environment for version >=3.10.

.. code-block:: bash

   pip install -e ".[test]"
   ES_TEST_VERSION=7 pytest guillotina_audit/tests
   ES_TEST_VERSION=8 pytest guillotina_audit/tests
   ES_TEST_VERSION=9 pytest guillotina_audit/tests

By default the tests run an Elasticsearch fixture with version 9. Use
``ES_TEST_VERSION`` to select the Elasticsearch major version. Set it to
``6``, ``7``, ``8`` or ``9``; the test fixture maps those values to the pinned
Docker image used by this branch. ``ES_TEST_VERSION=6`` is available for older
release-line checks, but this branch does not support Elasticsearch 6.


Breaking changes in 3.0.0
-------------------------

- Python 3.10 or newer is required.
- Guillotina 7.0.0 or newer is required.
- The Python Elasticsearch client dependency is now 9.x
  (``elasticsearch[async]>=9.0.0,<10.0.0``).
