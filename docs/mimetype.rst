``collective.blueprint.jsonmigrator.mimetype``
==============================================

Sometimes we need to fix/change mimetype of migrated object.

Parameters
----------

No parameters.

Expected data in pipeline:

    * **_path**: path to object on which we want to change mimetype.
    * **_content_type**: mimetype to be applied to object resolved above.

Example
-------

Configuration::

    [tranmogrifier]
    pipeline =
        source
        mimetype

    ...

    [mimetype]
    blueprint = collective.blueprint.jsonmigrator.mimetype

Data in pipeline::

    {
        "_path": "/Plone/index_html", 
        "_content_type": "text/html", 
    }
