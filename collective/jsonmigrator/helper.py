
import urllib
from zope.interface import Interface
from zope.schema import URI
from zope.schema import Int
from zope.schema import List
from zope.schema import Choice
from zope.schema import TextLine
from zope.schema import ASCIILine
from zope.schema.vocabulary import SimpleVocabulary
from z3c.form import form
from z3c.form import field
from z3c.form import button
from z3c.form import interfaces
from plone.z3cform.layout import wrap_form
from collective.transmogrifier.transmogrifier import configuration_registry
from collective.transmogrifier.transmogrifier import _load_config
from collective.jsonmigrator.remotesource import RemoteSource
from collective.jsonmigrator import JSONMigratorMessageFactory as _



class IJSONMigratorRun(Interface):
    """ remote source interface
    """

    config = TextLine()

    remote_url = URI(
            title=_(u"URL"),
            description=_(u"URL for the remote site that will provide the "
                          u"content to be imported and migrated "),
            required=True,
            )

    remote_username = ASCIILine(
            title=_(u"Username"),
            description=_(u"Username to log in to the remote site "),
            required=True,
            )

    remote_password = TextLine(
            title=_(u"Password"),
            description=_(u"Password to log in to the remote site "),
            required=True,
            )

    remote_path = TextLine(
            title=_(u"Start path"),
            description=_(u"Path where to start crawling and importing "
                          u"into current location."),
            required=True,
            )

    remote_crawl_depth = Int(
            title=_(u"Crawl depth"),
            description=_(u"How deep should we crawl remote site"),
            required=True,
            )

    remote_skip_path = List(
            title=_(u"Paths to skip"),
            description=_(u"Which paths to skip when crawling."),
            value_type=TextLine(),
            required=True,
            )


class JSONMigratorRun(form.Form):

    label = _(u"Synchronize and migrate")
    fields = field.Fields(IJSONMigratorRun)
    ignoreContext = True

    def updateWidgets(self):
        config = _load_config(self.request.get('form.widgets.config'))
        section = None
        for section_id in config.keys():
            tmp = config[section_id]
            if tmp.get('blueprint', '') == RemoteSource.name:
                section = tmp
                break
        if not section:
            raise Exception("Section with blueptint '%s' not found!" %
                    RemoteSource.__name__)
        for option, default in RemoteSource._options:
            field = self.fields.get(option.replace('-', '_'))
            default = section.get(option, default)
            if field.__name__ in ['remote_password', 'remote_path']:
                default = unicode(default)
            elif field.__name__ == 'remote_skip_path':
                default = [unicode(i) for i in default.split()]
            elif field.__name__ == 'remote_crawl_depth':
                default = int(default)
            field.field.default = default
        super(JSONMigratorRun, self).updateWidgets()
        self.widgets['config'].mode = interfaces.HIDDEN_MODE

    @button.buttonAndHandler(u'Run')
    def handleRun(self, action):
        data, errors = self.extractData()
        if errors:
            return False
        import ipdb; ipdb.set_trace()


class JSONMigratorConfigurations(object):

    def __call__(self, context):
        terms = []
        for conf_id in configuration_registry.listConfigurationIds():
            conf_file = _load_config(conf_id)
            for section_id in conf_file.keys():
                section = conf_file[section_id]
                if section.get('blueprint', '') == RemoteSource.name:
                    conf = configuration_registry.getConfiguration(conf_id)
                    terms.append(SimpleVocabulary.createTerm(
                            conf_id, conf_id, conf['title']))
                    break
        return SimpleVocabulary(terms)


class IJSONMigrator(Interface):
    """ remote source interface """

    config = Choice(
            title=_(u"Select configuration"),
            description=_(u"Registered configurations to choose from."),
            vocabulary=u"collective-jsonmigrator-configurations",
            )


class JSONMigrator(form.Form):

    label = _(u"Synchronize and migrate")
    fields = field.Fields(IJSONMigrator)

    ignoreContext = True

    @button.buttonAndHandler(u'Select')
    def handleSelect(self, action):
        data, errors = self.extractData()
        if errors:
            return False
        self.request.RESPONSE.redirect('%s/@@jsonmigrator-run?form.widgets.%s' %
                (self.context.absolute_url(), urllib.urlencode(data)))


JSONMigratorConfigurationsFactory = JSONMigratorConfigurations()
JSONMigratorRunView = wrap_form(JSONMigratorRun)
JSONMigratorView = wrap_form(JSONMigrator)
