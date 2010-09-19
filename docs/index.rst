collective.blueprint.jsonmigrator's documentation!
==================================================

List of blueprints built around ``collective.blueprints.jsonmigrator.source``
with purpose of providing flexible infrastructure to do migrations in Plone.

In source of this package in ``exports_scripts`` directory is also a helping
export script ``plone2.0_export.py`` which provides a external method
``export_plone20`` to export data from Plone 2.0 (script might also work with
higher versions of plone 2.1, 2.5, but was not tested) in format that is
suitable for ``collective.blueprints.jsonmigrator.source`` blueprint.

And if you might forgot, migration is a bitch ... so have fun :P

Avaliable blueprints
====================

.. toctree::
    :maxdepth: 1

    jsonsource
    skipitems
    partialcommit
    statistics
    workflowhistory
    mimetype
    properties
    permission_mapping
    owner
    ac_local_roles
    datafields

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

