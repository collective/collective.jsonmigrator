from zope.schema import URI
from zope.schema import ASCIILine
from zope.schema import TextLine
from zope.interface import Interface

from plone.z3cform.layout import wrap_form
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from collective.jsonmigrator import JSONMigratorMessageFactory as _


class IControlPanel(Interface):
    """ jsonmigrator settings """

    remoteurl = URI(
        title=_(u"Remote site"),
        description=_(u"URL for the remote site that will provide the "
                      u"content to be imported and migrated "),
        required=True,
        )

    username = ASCIILine(
        title=_(u"Username"),
        description=_(u"Username to log in to the remote site "),
        required=True,
        )

    password = TextLine(
        title=_(u"Password"),
        description=_(u"Password to log in to the remote site "),
        required=True,
        )


class ControlPanel(RegistryEditForm):
    """ jsonmigrator control panel """

    schema = IControlPanel
    schema_prefix = 'collective.jsonmigrator'

    label = _(u"Synchronize and migrate")
    description = _(u"Please enter the appropriate settings"
                    u"for the remote portal")


ControlPanelView = wrap_form(ControlPanel, ControlPanelFormWrapper)
ControlPanelView.label = u"JSONMigrator Settings"
