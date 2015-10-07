``collective.jsonmigrator.owner``
===========================================

Update owner of an object.

Parameters
----------

No parameters.

Expected data in pipeline:

    * **_path**: path to object on which we want to change properties.
    * **_owner**: properties to be applied to object resolved above.

Example
-------

Configuration::

    [transmogrifier]
    pipeline =
        source
        owner

    ...

    [owner]
    blueprint = collective.jsonmigrator.owner

Data in pipeline::

    {
        "_path": "/Plone/index_html",
        "_owner": [
            1,
            "admin"
        ],
    }


