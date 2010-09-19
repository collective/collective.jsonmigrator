``collective.blueprint.jsonmigrator.permission_mapping``
========================================================

Update permissions of an object.

Parameters
----------

No parameters.

Expected data in pipeline:

    * **_path**: path to object on which we want to change permissions.
    * **_permission_mapping**: permissions to be applied to object resolved above.

Example
-------

Configuration::

    [tranmogrifier]
    pipeline =
        source
        permission_mapping

    ...

    [mimetype]
    blueprint = collective.blueprint.jsonmigrator.permission_mapping

Data in pipeline::

    {
        "_path": "/Plone/index_html", 
        "_permission_mapping": {
            "Modify portal content": {
                "acquire": false, 
                "roles": [
                    "Manager", 
                    "Owner"
                ]
            }, 
            "Access contents information": {
                "acquire": true, 
                "roles": [
                    "Anonymous", 
                    "Manager", 
                    "Reviewer"
                ]
            }, 
            "View": {
                "acquire": true, 
                "roles": [
                    "Anonymous", 
                    "Manager", 
                    "Reviewer"
                ]
            }
        },
    }

