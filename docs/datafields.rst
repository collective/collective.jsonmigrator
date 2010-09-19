``collective.blueprint.jsonmigrator.datafields``
================================================

Update datefiels roles of an object.

:TODO: missing base path (maybe even passed somehow from source blueprint)
:TODO: only update if needed

Parameters
----------

No parameters.

    * **_path**: path to object on which we want to change local roles.
    * **_datafield_<field>**: field which needs to store data

Example
-------

Configuration::

    [tranmogrifier]
    pipeline =
        source
        datafields

    ...

    [datafields]
    blueprint = collective.blueprint.jsonmigrator.datafields

Data in pipeline::

    {
        "_path": "/Plone/index_html", 
        "_datafield_attachment": "0/1.json-file-1",
    }
    

