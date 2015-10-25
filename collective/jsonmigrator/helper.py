# -*- coding: utf-8 -*-
from collective.jsonmigrator import logger
from collective.jsonmigrator import msgFact as _
from collective.transmogrifier.transmogrifier import _load_config
from collective.transmogrifier.transmogrifier import configuration_registry
from collective.transmogrifier.transmogrifier import Transmogrifier
from plone.z3cform.layout import wrap_form
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form import interfaces
from zope.interface import Interface
from zope.schema import ASCIILine
from zope.schema import Choice
from zope.schema import Int
from zope.schema import List
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import URI
from zope.schema.interfaces import IFromUnicode, IList
from zope.schema.vocabulary import SimpleVocabulary

import urllib

SOURCE_SECTIONS = ['collective.jsonmigrator.remotesource',
                   'collective.jsonmigrator.catalogsource']


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
        required=False,
    )

    catalog_path = TextLine(
        title=_(u"Catalog Path"),
        description=_(u"The absolute path of the catalog tool."),
        required=True,
    )

    catalog_query = Text(
        title=_(u"Catalog Query"),
        description=_("Specify query parameters in dict notation. If left "
                      "empty, all items will be returned."),
        required=False,
    )


class JSONMigratorRun(form.Form):

    label = _(u"Synchronize and migrate")
    fields = field.Fields(IJSONMigratorRun)
    ignoreContext = True

    def updateWidgets(self):
        self.label = self.request.get('form.widgets.config')
        config = _load_config(self.request.get('form.widgets.config'))
        section = None
        for section_id in config.keys():
            tmp = config[section_id]
            if tmp.get('blueprint', '') in SOURCE_SECTIONS:
                section = tmp
                break
        if not section:
            raise Exception("Source section not found.")

        # Omit some fields depending on the selected source
        if section['blueprint'] == 'collective.jsonmigrator.catalogsource':
            self.fields = self.fields.omit('remote_path',
                                           'remote_crawl_depth',
                                           'remote_skip_path')
        elif section['blueprint'] == 'collective.jsonmigrator.remotesource':
            self.fields = self.fields.omit('catalog_path', 'catalog_query')

        # Fill in default values from the transmogrifier config file
        for option, value in section.items():
            field = self.fields.get(option.replace('-', '_'))
            if field:
                field = field.field
                value = value.decode('utf8')
                if IFromUnicode.providedBy(field):
                    field.default = field.fromUnicode(value)
                elif IList.providedBy(field):
                    field.default = [field.value_type.fromUnicode(v) for v
                                     in value.split()]

        super(JSONMigratorRun, self).updateWidgets()
        self.widgets['config'].mode = interfaces.HIDDEN_MODE

    @button.buttonAndHandler(u'Run')
    def handleRun(self, action):
        data, errors = self.extractData()
        if errors:
            return False
        self._run(data)

    @button.buttonAndHandler(u'Run & Next')
    def handleRunAndNext(self, action):
        data, errors = self.extractData()
        if errors:
            return False
        self._run(data)

        configs = configuration_registry.listConfigurationIds()
        current_config = data.get('config')
        if configs.index(current_config) + 2 > len(configs):
            # This was the last config
            self._redirect('@@jsonmigrator', current_config)

        else:
            next_config = configs[configs.index(current_config) + 1]
            self._redirect('@@jsonmigrator-run', next_config)

    @button.buttonAndHandler(u'Back')
    def handleBack(self, action):
        data, errors = self.extractData()
        params = urllib.urlencode({'form.widgets.config': data.get('config')})
        self.request.RESPONSE.redirect('/'.join((
            self.context.absolute_url(),
            '@@jsonmigrator',
            '?%s' % params)))

    def _run(self, data):
        logger.info("Start importing profile: " + data['config'])
        Transmogrifier(self.context)(data['config'])
        logger.info("Stop importing profile: " + data['config'])
        IStatusMessage(self.request).addStatusMessage(
            'Migrated: %s' % data['config'], type='info')

    def _redirect(self, viewname, config_id):
        if isinstance(config_id, unicode):
            config_id = config_id.encode('utf-8')
        params = urllib.urlencode({'form.widgets.config': config_id})
        return self.request.RESPONSE.redirect('/'.join((
            self.context.absolute_url(),
            viewname,
            '?%s' % params)))


class JSONMigratorConfigurations(object):

    def __call__(self, context):
        terms = []
        for conf_id in configuration_registry.listConfigurationIds():
            conf_file = _load_config(conf_id)
            for section_id in conf_file.keys():
                section = conf_file[section_id]
                if section.get('blueprint', '') in SOURCE_SECTIONS:
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
        self.request.RESPONSE.redirect(
            '%s/@@jsonmigrator-run?form.widgets.%s' %
            (self.context.absolute_url(), urllib.urlencode(data)))


JSONMigratorConfigurationsFactory = JSONMigratorConfigurations()
JSONMigratorRunView = wrap_form(JSONMigratorRun)
JSONMigratorView = wrap_form(JSONMigrator)
