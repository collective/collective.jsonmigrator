``collective.blueprint.jsonmigrator.skipitems``
===============================================

Skip first N item in pipeline.

Development blueprint. Usefull when you are proccessing big data pipelines and
you know first N items are already migrated.

Parameters
----------

:first (required): 
    define number of items from the beggining of data pipeline to skip.

Example
-------

Configuration::

    [tranmogrifier]
    pipeline =
        source
        skipitems

    ...

    [skipitems]
    blueprint = collective.blueprint.jsonmigrator.skipitems
    first = 10000
