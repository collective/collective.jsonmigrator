collective.blueprint.jsonmigrator's documentation!
==================================================

The purpose of the ``collective.blueprint.jsonmigrator`` package is to provide
a set of
blueprints that help you to migrate content into `Plone`_. (``blueprint`` is
an extension to `collective.transmogrifier`_).

It provides a list of blueprints built around
``collective.blueprints.jsonmigrator.source``
with the purpose of providing flexible infrastructure to do migrations in Plone.

In the ``exports_scripts`` directory of this package, there is an
export script :doc:`plone2.0_export` which provides an external method
``export_plone20`` to export data from Plone 2.0 (script might also work with
higher versions of plone 2.1, 2.5, but was not tested) in a format that is
suitable for the ``collective.blueprints.jsonmigrator.source`` blueprint.

And if you might forgot, migration is a bitch ... so have fun :P

.. toctree::
    :titlesonly:

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

