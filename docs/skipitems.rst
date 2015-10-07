``collective.jsonmigrator.skipitems``
===============================================

Skip first N item in pipeline.

Development blueprint. Useful when you are processing big data pipelines and
you know that the first N items are already migrated.

Parameters
----------

:first (required):
    define number of items from the beginning of data pipeline to skip.

Example
-------

Configuration::

    [transmogrifier]
    pipeline =
        source
        skipitems

    ...

    [skipitems]
    blueprint = collective.jsonmigrator.skipitems
    first = 10000
