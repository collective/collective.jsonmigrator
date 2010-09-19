``collective.blueprint.jsonmigrator.ac_local_roles``
====================================================

Update local roles of an object.

Parameters
----------

No parameters.

    * **_path**: path to object on which we want to change local roles.
    * **_ac_local_roles**: local roles to be applied to object resolved above.

Example
-------

Configuration::

    [tranmogrifier]
    pipeline =
        source
        ac_local_roles

    ...

    [ac_local_roles]
    blueprint = collective.blueprint.jsonmigrator.ac_local_roles

Data in pipeline::

    {
        "_path": "/Plone/index_html", 
        "_ac_local_roles": {
            "admin": [
                "Owner"
            ]
        },
    }
    

