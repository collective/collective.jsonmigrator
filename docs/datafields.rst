``collective.jsonmigrator.datafields``
================================================

Update data/blob fields of an object.

:TODO: missing base path (maybe even passed somehow from source blueprint)
:TODO: only update if needed

Configuration options
---------------------

No specific blueprint parameters.

Expected data structure in pipeline:

    * **_path**: path to object on which we want to change local roles.
    * **_datafield_<field>**: field which needs to store data

Example
-------

This example will try to store content of ``0/1.json-file-1`` into the
``attachment`` field of the ``/Plone/index_html`` object.

Configuration::

    [transmogrifier]
    pipeline =
        source
        datafields

    ...

    [datafields]
    blueprint = collective.jsonmigrator.datafields

Data in pipeline::

    {
        "_path": "/Plone/index_html",
        "_datafield_attachment": "0/1.json-file-1",
    }
