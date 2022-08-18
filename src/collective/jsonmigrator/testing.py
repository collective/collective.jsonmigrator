from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer

import collective.jsonmigrator
import plone.app.multilingual


class CollectiveJsonmigratorLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):  # @UnusedVariable
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.jsonmigrator)


JSONMIGRATOR_FIXTURE = CollectiveJsonmigratorLayer()


class CollectiveJsonmigratorPAMLayer(PloneSandboxLayer):

    defaultBases = (JSONMIGRATOR_FIXTURE,)

    def setUpZope(self, app, configurationContext):  # @UnusedVariable
        self.loadZCML(package=plone.app.multilingual)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.app.multilingual:default")


JSONMIGRATOR_PAM_FIXTURE = CollectiveJsonmigratorPAMLayer()


JSONMIGRATOR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(JSONMIGRATOR_FIXTURE,),
    name="CollectiveJsonmigratorLayer:IntegrationTesting",
)

JSONMIGRATOR_PAM_INTEGRATION_TESTING = IntegrationTesting(
    bases=(JSONMIGRATOR_PAM_FIXTURE,),
    name="CollectiveJsonmigratorPAMLayer:IntegrationTesting",
)

JSONMIGRATOR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(JSONMIGRATOR_FIXTURE,),
    name="CollectiveJsonmigratorLayer:FunctionalTesting",
)
