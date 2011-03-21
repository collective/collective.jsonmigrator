
import urllib
from zope.interface import Interface
from zope.schema import URI
from zope.schema import Int
from zope.schema import List
from zope.schema import Choice
from zope.schema import TextLine
from zope.schema import ASCIILine
from zope.schema import Bool
from zope.schema import Text
from zope.schema import URI
from zope.schema.vocabulary import SimpleVocabulary
from z3c.form import form
from z3c.form import field
from z3c.form import button
from z3c.form import group
from z3c.form import interfaces
from z3c.form.browser import multi
from plone.app.z3cform.layout import wrap_form
from collective.transmogrifier.transmogrifier import Transmogrifier
from collective.transmogrifier.transmogrifier import configuration_registry
from collective.transmogrifier.transmogrifier import _load_config
from collective.jsonmigrator.remotesource import RemoteSource
from collective.jsonmigrator import JSONMigratorMessageFactory as _
from collective.jsonmigrator import logger



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

groupforms = {}

def formfactory(configname):
    if configname in groupforms:
        return groupforms[configname]
    groups = []
    config = _load_config(configname)
    sections = config['transmogrifier']['pipeline'].splitlines()
    print sections
    for section_id in sections:
        if not section_id:
            continue
        if section_id == 'transmogrifier':
            continue
        cparser = config[section_id]
        g = type(section_id, (group.Group,),dict(label=section_id.capitalize()))
        fields = []
        doc = cparser.get('@doc','')
        for key,value in cparser.items():
            if key in ['@doc','blueprint']:
                continue
            if key.startswith('@'):
                key = key[1:]
                metavar,_,help = value.partition(':')
                default = unicode(cparser.get(key,''))
                help = value
            else:
                if '@'+key in cparser:
                    # let the @option line be used instead
                    continue
                else:
                    metavar = 'LINE'
                    default = unicode(value)
                    help = ''
            title = key.capitalize().replace('-',' ').replace('_',' ')
#                name = "%s:%s"%(section_id,key[1:])
            if metavar == 'HIDDEN':
                continue
            elif metavar == 'INT':
                ftype = Int()
                if default:
                    default = int(default)
                else:
                    default = 0
            #elif metavar == 'URL':
            #    ftype = URI()
            elif metavar == 'LIST' or '\n' in default:
                ftype = List(
                    value_type=TextLine(),)
                #ftype = Text()
                #if type(default) == type(""):
                default = default.splitlines()
                ftype.widgetFactory = multi.multiFieldWidgetFactory
            elif metavar.upper() != metavar:
                ftype = Bool()
                default = len(default)
            else:
                ftype = TextLine()
            ftype.__name__=title
            ftype.title=unicode(title)
            ftype.description=unicode(help)
            ftype.required=False
            ftype.default = default
            print (key,value,ftype,default)
            fields.append(ftype)
        if fields:
            g.fields = field.Fields(*fields)
            groups.append(g)
    groupforms[configname]=groups
    return groups


class JSONMigratorRun(group.GroupForm, form.Form):

    label = _(u"Synchronize and migrate")
    fields = field.Fields(IJSONMigratorRun)
    ignoreContext = True

    def update(self):
        configname = self.request.get('form.widgets.config')
        self.groups = formfactory(configname)
        return super(JSONMigratorRun, self).update()

    @property
    def fields(self):
        fields = [TextLine(__name__='config')]
        return field.Fields(*fields)


    def updateWidgets(self):
        super(JSONMigratorRun, self).updateWidgets()
        self.widgets['config'].mode = interfaces.HIDDEN_MODE

    @button.buttonAndHandler(u'Run')
    def handleRun(self, action):
        import ipdb; ipdb.set_trace()
        data, errors = self.extractData()
        if errors:
            return False

        logger.info("Start importing profile: " + data['config'])
        Transmogrifier(self.context)(data['config'])
        logger.info("Stop importing profile: " + data['config'])


class JSONMigratorConfigurations(object):

    def __call__(self, context):
        terms = []
        for conf_id in configuration_registry.listConfigurationIds():
            conf_file = _load_config(conf_id)
            for section_id in conf_file.keys():
                section = conf_file[section_id]
                if section.get('blueprint', '') == 'plone.app.transmogrifier.atschemaupdater':
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
