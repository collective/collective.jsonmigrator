``collective.blueprint.jsonmigrator.properties``
================================================

Update properties of an object.

Parameters
----------

No parameters.

Expected data in pipeline:

    * **_path**: path to object on which we want to change properties.
    * **_properties**: properties to be applied to object resolved above.

Example
-------

Configuration::

    [tranmogrifier]
    pipeline =
        source
        properties

    ...

    [properties]
    blueprint = collective.blueprint.jsonmigrator.properties

Data in pipeline::

    {
        "_path": "/Plone/index_html", 
        "_properties": [
            [
                "title", 
                "Welcome to Plone", 
                "string"
            ]
        ],
    }

