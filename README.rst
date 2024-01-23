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

`pip install guillotina-audit`


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
