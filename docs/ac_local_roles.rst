``collective.jsonmigrator.local_roles``
=======================================

Update local roles of an object.

Parameters
----------

No parameters.

    * **_path**: path to object on which we want to change local roles.
    * **_ac_local_roles**: local roles to be applied to object resolved above.

Example
-------

Configuration::

    [transmogrifier]
    pipeline =
        source
        local_roles

    ...

    [local_roles]
    blueprint = collective.jsonmigrator.local_roles

Data in pipeline::

    {
        "_path": "/Plone/index_html",
        "_ac_local_roles": {
            "admin": [
                "Owner"
            ]
        },
    }


