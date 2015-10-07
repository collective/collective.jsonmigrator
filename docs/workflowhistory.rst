``collective.jsonmigrator.workflowhistory``
=====================================================

Update the workflow history of an object.

Parameters
----------

No parameters.

Expected data in pipeline:

    * **_path**: path to object on which we want to change workflow history.
    * **_workflow_history**: workflow history to be applied to object resolved above.
Example
-------

Configuration::

    [transmogrifier]
    pipeline =
        source
        workflowhistory

    ...

    [workflowhistory]
    blueprint = collective.jsonmigrator.workflowhistory

Data in pipeline::

    {
        "_path": "/Plone/index_html",
        "_workflow_history": {
            "plone_workflow": [
                {
                    "action": null,
                    "review_state": "visible",
                    "comments": "",
                    "actor": "admin",
                    "time": "2010/09/15 02:19:57.932 GMT+2"
                }
            ]
        },
    }

