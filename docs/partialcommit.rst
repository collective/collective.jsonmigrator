``collective.blueprint.jsonmigrator.partialcommit``
===================================================

Used to commit after some items have been processed.

Parameters
----------

:every (required): 
    Define number of items after which commit (writing to ZODB) will happen.

Example
-------

Configuration::

    [tranmogrifier]
    pipeline =
        source
        commit

    ...

    [commit]
    blueprint = collective.blueprint.jsonmigrator.partialcommit
    every = 500
