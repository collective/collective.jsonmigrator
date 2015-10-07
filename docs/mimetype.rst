``collective.jsonmigrator.mimetype``
==============================================

Sometimes we need to fix/change the mimetype of migrated objects.

Parameters
----------

No parameters.

Expected data in pipeline:

    * **_path**: path to object on which we want to change mimetype.
    * **_content_type**: mimetype to be applied to object resolved above.

Example
-------

Configuration::

    [transmogrifier]
    pipeline =
        source
        mimetype

    ...

    [mimetype]
    blueprint = collective.jsonmigrator.mimetype

Data in pipeline::

    {
        "_path": "/Plone/index_html",
        "_content_type": "text/html",
    }
