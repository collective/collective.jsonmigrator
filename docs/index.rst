collective.blueprint.jsonmigrator's documentation!
==================================================

Purpose of ``collective.blueprint.jsonmigrator`` package is to provide set of
blueprints that help you migrate content into `Plone`_. (``blueprint`` is
extension to `collective.transmogrifier`_).

List of blueprints built around ``collective.blueprints.jsonmigrator.source``
with purpose of providing flexible infrastructure to do migrations in Plone.

In source of this package in ``exports_scripts`` directory is also a helping
export script :doc:`plone2.0_export` which provides a external method
``export_plone20`` to export data from Plone 2.0 (script might also work with
higher versions of plone 2.1, 2.5, but was not tested) in format that is
suitable for ``collective.blueprints.jsonmigrator.source`` blueprint.

And if you might forgot, migration is a bitch ... so have fun :P

.. toctree::
    :titlesonly:
    :hidden:

    jsonsource <jsonsource>
    skipitems <skipitems>
    partialcommit <partialcommit>
    statistics <statistics>
    workflowhistory <workflowhistory>
    mimetype <mimetype>
    properties <properties>
    permission_mapping <permission_mapping>
    owner <owner>
    ac_local_roles <ac_local_roles>
    datafields <datafields>

.. _`collective.transmogrifier`: http://pypi.python.org/pypi/collective.transmogrifier
.. _`Plone`: http://plone.org

