``collective.jsonmigrator.partialcommit``
===================================================

Used to commit after some items have been processed.

Parameters
----------

:every (default: 100):
    Define number of items after which commit (writing to ZODB) will happen.

Example
-------

Configuration::

    [transmogrifier]
    pipeline =
        source
        commit

    ...

    [commit]
    blueprint = collective.jsonmigrator.partialcommit
    every = 500
