``collective.jsonmigrator.properties``
================================================

Update properties of an object.

Configuration options
---------------------

No specific blueprint parameters.

Expected data structure in pipeline:

    * **_path**: path to object on which we want to change properties.
    * **_properties**: properties to be applied to object resolved above.

        properties passed in this data field (as shown in example) is a list of
        3-item lists.::

            [
                [
                    <property-name>,
                    <property-value>,
                    <property-type>
                ],
                [
                    <property2-name>,
                    <property2-value>,
                    <property2-type>
                ],
                ...
            ]

        ``<property-type>`` is set of types which you can select through the
        ZMI when you edit/add a property.

Example
-------

Configuration::

    [transmogrifier]
    pipeline =
        source
        properties

    ...

    [properties]
    blueprint = collective.jsonmigrator.properties

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

