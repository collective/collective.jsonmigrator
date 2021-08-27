``collective.jsonmigrator.translations``
===========================================

Update translations of plone.app.multilingual.

Parameters
----------

No parameters.

Expected data in pipeline:

    * **_path**: path to object on which we want to set the translations.
    * **_translations**: dictionary containing the uids of translations objects . The uids of the translations objects in the portal must be the same as they are in json.

Example
-------

Configuration::

    [transmogrifier]
    pipeline =
        source
        translations

    ...

    [translations]
    blueprint = collective.jsonmigrator.translations

Data in pipeline::

    {
        "_path": "/Plone/index_html",
        "_translations": {
            "es": "823919aca5ca43828ee7b52de167b1b7",
            "pt-br": "1ea13a3b5c1e4c12b5d8c262cecb5729"
        },
    }
