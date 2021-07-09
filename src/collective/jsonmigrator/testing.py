# -*- coding: utf-8 -*-
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer

import collective.jsonmigrator


class CollectiveJsonmigratorLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.jsonmigrator)


COLLECTIVE_JSONMIGRATOR_FIXTURE = CollectiveJsonmigratorLayer()


COLLECTIVE_JSONMIGRATOR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_JSONMIGRATOR_FIXTURE,),
    name='CollectiveJsonmigratorLayer:IntegrationTesting',
)


COLLECTIVE_JSONMIGRATOR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_JSONMIGRATOR_FIXTURE,),
    name='CollectiveJsonmigratorLayer:FunctionalTesting',
)
