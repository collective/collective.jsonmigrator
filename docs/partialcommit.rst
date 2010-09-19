``collective.blueprint.jsonmigrator.partialcommit``
===================================================

Used to commit after some items are being proccesed.

Parameters
----------

:every (required): 
    Define number after commit (writing to ZODB) will happen.

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
