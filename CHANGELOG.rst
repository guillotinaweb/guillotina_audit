2.0.3 (2024-03-06)
------------------

- Adding permissions_changed action when permissions are changed


2.0.2 (2024-03-06)
------------------

- Being able to setting up index_permission_changes in settings. If
  defined as True, it will index all changes in permissions.


2.0.1 (2024-03-05)
------------------

- Being able to decode dates and datetimes when indexing custom
  payloads from events.


2.0.0 (2024-01-23)
------------------

- Supporting ES version 7 and 8
- By default the async elasticsearch version is 8.12


1.0.6 (2023-12-19)
------------------

- Changing date by datetime in models.
- Fixing creation_date was not indexed when login wildcards


1.0.5 (2023-12-12)
------------------

- Adding log_entry method to the utility. Now customized documents can
  be indexed

  
1.0.4 (2023-11-16)
------------------

- Changing requirement of guillotina


1.0.3 (2023-11-16)
------------------

- Adding try except clause in subscribers


1.0.2 (2023-11-15)
------------------

- Adding save_payload parameter in the settings of the utility


1.0.1 (2023-11-15)
------------------

- Solving bugs


1.0.0 (2023-11-15)
------------------

- Initial release
  [nilbacardit26]
