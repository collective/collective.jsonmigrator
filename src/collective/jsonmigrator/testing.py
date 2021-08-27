# -*- coding: utf-8 -*-
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from Products.CMFPlone.utils import getFSVersionTuple

import collective.jsonmigrator
import plone.app.multilingual


version_tuple = getFSVersionTuple()
PLONE_VERSION = float("{0}.{1}".format(version_tuple[0], version_tuple[1]))


class CollectiveJsonmigratorLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):  # @UnusedVariable
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.jsonmigrator)

    def setUpPloneSite(self, portal):
        if PLONE_VERSION == 5.1:
            applyProfile(portal, "plone.app.contenttypes:default")


COLLECTIVE_JSONMIGRATOR_FIXTURE = CollectiveJsonmigratorLayer()


class CollectiveJsonmigratorPAMLayer(PloneSandboxLayer):

    defaultBases = (COLLECTIVE_JSONMIGRATOR_FIXTURE,)

    def setUpZope(self, app, configurationContext):  # @UnusedVariable
        self.loadZCML(package=plone.app.multilingual)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.app.multilingual:default")


COLLECTIVE_JSONMIGRATOR_PAM_FIXTURE = CollectiveJsonmigratorPAMLayer()


COLLECTIVE_JSONMIGRATOR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_JSONMIGRATOR_FIXTURE,),
    name="CollectiveJsonmigratorLayer:IntegrationTesting",
)

COLLECTIVE_JSONMIGRATOR_PAM_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_JSONMIGRATOR_PAM_FIXTURE,),
    name="CollectiveJsonmigratorPAMLayer:IntegrationTesting",
)

COLLECTIVE_JSONMIGRATOR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_JSONMIGRATOR_FIXTURE,),
    name="CollectiveJsonmigratorLayer:FunctionalTesting",
)
