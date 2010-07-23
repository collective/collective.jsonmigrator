###############################################################################
#####                                                                     #####
#####   IMPORTANT, READ THIS !!!                                          #####
#####   ------------------------                                          #####
#####                                                                     #####
#####   Bellow is the external method which you enable by adding it       #####
#####   into your Plone site.                                             #####
#####                                                                     #####
###############################################################################

import os
import shutil
import simplejson
from datetime import datetime
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName

COUNTER = 1
HOMEDIR = '/opt/plone/unex_exported_data'
CLASSNAME_TO_SKIP_LAUD = ['ControllerPythonScript',
    'ControllerPageTemplate', 'ControllerValidator', 'PythonScript', 'SQL', 'Connection',
    'ZetadbScript', 'ExternalMethod', 'ZetadbSqlInsert', 'ZetadbMysqlda', 'SiteRoot',
    'ZetadbApplication', 'ZetadbZptInsert', 'I18NLayer', 'ZetadbZptView', 'BrowserIdManager',
    'ZetadbScriptSelectMaster', 'ZetadbSqlSelect', ]
CLASSNAME_TO_SKIP = ['CatalogTool', 'MemberDataTool', 'SkinsTool', 'TypesTool',
    'UndoTool', 'URLTool', 'WorkflowTool', 'DiscussionTool', 'MembershipTool',
    'RegistrationTool', 'PropertiesTool', 'MetadataTool', 'SyndicationTool',
    'PloneTool', 'NavigationTool', 'FactoryTool', 'FormTool', 'MigrationTool',
    'CalendarTool', 'QuickInstallerTool', 'GroupsTool', 'GroupDataTool', 'MailHost',
    'CookieCrumbler', 'ContentTypeRegistry', 'GroupUserFolder', 'CachingPolicyManager',
    'InterfaceTool', 'PloneControlPanel', 'FormController', 'SiteErrorLog', 'SinTool',
    'ArchetypeTool', 'RAMCacheManager', 'PloneArticleTool', 'SyndicationInformation',
    'ActionIconsTool', 'AcceleratedHTTPCacheManager', 'ActionsTool', 'UIDCatalog',
    'ReferenceCatalog', 'ContentPanelsTool', ]
ID_TO_SKIP = ['Members', ]


def export_plone20(self):

    global COUNTER
    global TMPDIR
    global ID_TO_SKIP

    COUNTER = 1
    TODAY = datetime.today()
    TMPDIR = HOMEDIR+'/content_'+self.getId()+'_'+TODAY.strftime('%Y-%m-%d-%H-%M-%S')

    id_to_skip = self.REQUEST.get('id_to_skip', None)
    if id_to_skip is not None:
        ID_TO_SKIP += id_to_skip.split(',')

    if os.path.isdir(TMPDIR):
        shutil.rmtree(TMPDIR)
    else:
        os.mkdir(TMPDIR)

    write(walk(self))

    # TODO: we should return something more useful
    return 'SUCCESS :: '+self.absolute_url()+'\n'


def walk(folder):
    for item_id in folder.objectIds():
        item = folder[item_id]
        if item.__class__.__name__ in CLASSNAME_TO_SKIP or \
           item.getId() in ID_TO_SKIP:
            continue
        if item.__class__.__name__ in CLASSNAME_TO_SKIP_LAUD:
            print '>> SKIPPING :: ['+item.__class__.__name__+'] '+item.absolute_url()
            continue
        yield item
        if getattr(item, 'objectIds', None) and \
           item.objectIds():
            for subitem in walk(item):
                yield subitem


def write(items):
    global COUNTER

    for item in items:
        if item.__class__.__name__ not in CLASSNAME_TO_WAPPER_MAP.keys():
            import pdb; pdb.set_trace()
            raise Exception, 'No wrapper defined for "'+item.__class__.__name__+ \
                                                  '" ('+item.absolute_url()+').'
        write_to_jsonfile(CLASSNAME_TO_WAPPER_MAP[item.__class__.__name__](item))
        COUNTER += 1


def write_to_jsonfile(item):
    global COUNTER

    SUB_TMPDIR = os.path.join(TMPDIR, str(COUNTER/1000)) # 1000 files per folder, so we dont reach some fs limit
    if not os.path.isdir(SUB_TMPDIR):
        os.mkdir(SUB_TMPDIR)

    # we store data fields in separate files
    datafield_counter = 1
    if '__datafields__' in item.keys():
        for datafield in item['__datafields__']:
            datafield_filepath = os.path.join(SUB_TMPDIR, str(COUNTER)+'.json-file-'+str(datafield_counter))
            f = open(datafield_filepath, 'wb')
            f.write(item[datafield])
            item[datafield] = os.path.join(str(COUNTER/1000), str(COUNTER)+'.json-file-'+str(datafield_counter))
            f.close()
            datafield_counter += 1
        item.pop(u'__datafields__')

    f = open(os.path.join(SUB_TMPDIR, str(COUNTER)+'.json'), 'wb')
    simplejson.dump(item, f, indent=4)
    f.close()


def getPermissionMapping(acperm):
    result = {}
    for entry in acperm:
        result[entry[0]] = entry[1]
    return result


class BaseWrapper(dict):
    """Wraps the dublin core metadata and pass it as tranmogrifier friendly style
    """

    def __init__(self, obj):
        self.obj = obj

        self.portal = getToolByName(obj, 'portal_url').getPortalObject()
        self.portal_utils = getToolByName(obj, 'plone_utils')
        self.charset = self.portal.portal_properties.site_properties.default_charset

        if not self.charset: # newer seen it missing ... but users can change it
            self.charset = 'utf-8'

        self['__datafields__'] = []
        self['_path'] = '/'.join(self.obj.getPhysicalPath())

        self['_type'] = self.obj.__class__.__name__

        self['id'] = obj.getId()
        self['title'] = obj.title.decode(self.charset, 'ignore')
        self['description'] = obj.description.decode(self.charset, 'ignore')
        self['language'] = obj.language
        self['rights'] = obj.rights.decode(self.charset, 'ignore')
        # for DC attrs that are tuples
        for attr in ('subject', 'contributors'):
            self[attr] = []
            val_tuple = getattr(obj, attr, False)
            if val_tuple:
                for val in val_tuple:
                    self[attr].append(val.decode(self.charset, 'ignore'))
                self[attr] = tuple(self[attr])
        # for DC attrs that are DateTimes
        datetimes_dict = {'creation_date': 'creation_date',
                          'modification_date': 'modification_date',
                          'expiration_date': 'expirationDate',
                          'effective_date': 'effectiveDate'}
        for old_name, new_name in datetimes_dict.items():
            val = getattr(obj, old_name, False)
            if val:
                self[new_name] = str(val)

        # workflow history
        if hasattr(obj, 'workflow_history'):
            workflow_history = obj.workflow_history.data
            try:
                for w in workflow_history:
                    for i, w2 in enumerate(workflow_history[w]):
                        workflow_history[w][i]['time'] = str(workflow_history[w][i]['time'])
                        workflow_history[w][i]['comments'] = workflow_history[w][i]['comments'].decode(self.charset, 'ignore')
            except:
                import pdb; pdb.set_trace()
            self['_workflow_history'] = workflow_history

        # default view
        _browser = '/'.join(self.portal_utils.browserDefault(aq_base(obj))[1])
        if _browser not in ['folder_listing']:
            self['_layout'] = ''
            self['_defaultpage'] = _browser
        #elif obj.getId() != 'index_html':
        #    self['_layout'] = _browser
        #    self['_defaultpage'] = ''

        # format
        self['_content_type'] = obj.Format()

        # properties
        self['_properties'] = []
        if getattr(aq_base(obj), 'propertyIds', False):
            obj_base = aq_base(obj)
            for pid in obj_base.propertyIds():
                val = obj_base.getProperty(pid)
                typ = obj_base.getPropertyType(pid)
                if typ == 'string':
                    if getattr(val, 'decode', False):
                        try:
                            val = val.decode(self.charset, 'ignore')
                        except UnicodeEncodeError:
                            val = unicode(val)
                    else:
                        val = unicode(val)
                self['_properties'].append((pid, val,
                                       obj_base.getPropertyType(pid)))

        # local roles
        self['_ac_local_roles'] = {}
        if getattr(obj, '__ac_local_roles__', False):
            for key, val in obj.__ac_local_roles__.items():
                if key is not None:
                    self['_ac_local_roles'][key] = val

        self['_userdefined_roles'] = ()
        if getattr(aq_base(obj), 'userdefined_roles', False):
            self['_userdefined_roles'] = obj.userdefined_roles()

        self['_permission_mapping'] = {}
        if getattr(aq_base(obj), 'permission_settings', False):
            roles = obj.validRoles()
            ps = obj.permission_settings()
            for perm in ps:
                unchecked = 0
                if not perm['acquire']:
                    unchecked = 1
                new_roles = []
                for role in perm['roles']:
                    if role['checked']:
                        role_idx = role['name'].index('r')+1
                        role_name = roles[int(role['name'][role_idx:])]
                        new_roles.append(role_name)
                if unchecked or new_roles:
                    self['_permission_mapping'][perm['name']] = \
                         {'acquire': not unchecked,
                          'roles': new_roles}

#        self['_ac_inherited_permissions'] = {}
#        if getattr(aq_base(obj), 'ac_inherited_permissions', False):
#            oldmap = getPermissionMapping(obj.ac_inherited_permissions(1))
#            for key, values in oldmap.items():
#                old_p = Permission(key, values, obj)
#                self['_ac_inherited_permissions'][key] = old_p.getRoles()

        if getattr(aq_base(obj), 'getWrappedOwner', False):
            self['_owner'] = (1, obj.getWrappedOwner().getId())
        else:
            # fallback
            # not very nice but at least it works
            # trying to get/set the owner via getOwner(), changeOwnership(...)
            # did not work, at least not with plone 1.x, at 1.0.1, zope 2.6.2
            self['_owner'] = (0, obj.getOwner(info = 1).getId())


class DocumentWrapper(BaseWrapper):

    def __init__(self, obj):
        super(DocumentWrapper, self).__init__(obj)
        self['text'] = obj.text.decode(self.charset, 'ignore')


class I18NFolderWrapper(BaseWrapper):

    def __init__(self, obj):
        super(I18NFolderWrapper, self).__init__(obj)
        # We are ignoring another languages
        lang = obj.getDefaultLanguage()
        data = obj.folder_languages.get(lang, None)
        if data is not None:
            self['title'] = data['title'].decode(self.charset, 'ignore')
            self['description'] = data['description'].decode(self.charset, 'ignore')
        else:
            print 'ERROR: Cannot get default data for I18NFolder "%s"' % self['_path']

        # delete empty title in properties
        for prop in self['_properties']:
            propname, propvalue, proptitle = prop
            if propname == "title":
                self['_properties'].remove(prop)


        # Not lose information: generate properites es_title, en_title, etc.
        for lang in obj.folder_languages:
            data = obj.folder_languages[lang]
            for field in data:
                self['_properties'].append(['%s_%s' % (lang, field),
                                            data[field].decode(self.charset, 'ignore'),
                                            'text'])


class LinkWrapper(BaseWrapper):

    def __init__(self, obj):
        super(LinkWrapper, self).__init__(obj)
        self['remote_url'] = obj.remote_url


class NewsItemWrapper(DocumentWrapper):

    def __init__(self, obj):
        super(NewsItemWrapper, self).__init__(obj)
        self['text_format'] = obj.text_format


class ListCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ListCriteriaWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['value'] = obj.value
        self['operator'] = obj.operator


class StringCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(StringCriteriaWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['value'] = obj.value


class SortCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(SortCriteriaWrapper, self).__init__(obj)
        self['index'] = obj.index
        self['reversed'] = obj.reversed


class DateCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(DateCriteriaWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['value'] = obj.value
        self['operation'] = obj.operation
        self['daterange'] = obj.daterange


class FileWrapper(BaseWrapper):

    def __init__(self, obj):
        super(FileWrapper, self).__init__(obj)
        self['__datafields__'].append('_datafield_file')
        data = str(obj.data)
        if len(data) != obj.getSize():
            raise Exception, 'Problem while extracting data for File content type at '+obj.absolute_url()
        self['_datafield_file'] = data


class ImageWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ImageWrapper, self).__init__(obj)
        self['__datafields__'].append('_datafield_image')
        data = str(obj.data)
        if len(data) != obj.getSize():
            raise Exception, 'Problem while extracting data for Image content type at '+obj.absolute_url()
        self['_datafield_image'] = data


class EventWrapper(BaseWrapper):

    def __init__(self, obj):
        super(EventWrapper, self).__init__(obj)
        self['effective_date'] = str(obj.effective_date)
        self['expiration_date'] = str(obj.expiration_date)
        self['start_date'] = str(obj.start_date)
        self['end_date'] = str(obj.end_date)
        self['location'] = obj.location.decode(self.charset, 'ignore')
        self['contact_name'] = obj.contact_name.decode(self.charset, 'ignore')
        self['contact_email'] = obj.contact_email
        self['contact_phone'] = obj.contact_phone
        self['event_url'] = obj.event_url


class ArchetypesWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ArchetypesWrapper, self).__init__(obj)

        fields = obj.schema.fields()
        for field in fields:
            type_ = field.__class__.__name__
            if type_ in ['StringField', 'BooleanField', 'LinesField', 'IntegerField', 'TextField',
                         'SimpleDataGridField', 'FloatField', 'FixedPointField']:
                try:
                    value = field.get(obj)
                except:
                    try:
                        value = field.getRaw(obj)
                    except:
                        if field.getStorage().__class__.__name__ == 'PostgreSQLStorage':
                            continue
                        else:
                            import pdb; pdb.set_trace()
                if callable(value) is True:
                    value = value()
                if value:
                    self[unicode(field.__name__)] = value
            elif type_ in ['TALESString', 'ZPTField']:
                value = field.getRaw(obj)
                if value:
                    self[unicode(field.__name__)] = value
            elif type_ in ['DateTimeField']:
                value = str(field.get(obj))
                if value:
                    self[unicode(field.__name__)] = value
            elif type_ in ['ReferenceField']:
                value = field.get(obj)
                if value:
                    if field.multiValued:
                        self[unicode(field.__name__)] = ['/'+i.absolute_url() for i in value]
                    else:
                        self[unicode(field.__name__)] = value.absolute_url()
            elif type_ in ['ImageField', 'FileField']:
                fieldname = unicode('_data_'+field.__name__)
                value = field.get(obj)
                value2 = value
                if type(value) is not str:
                    value = str(value.data)
                if value:
                    size = value2.getSize()
                    self['__datafields__'].append(fieldname)
                    self[fieldname] = {
                        'data': value,
                        'size': size, }
            elif type_ in ['ComputedField']:
                pass
            else:
                raise 'Unknown field type for ArchetypesWrapper.'

    def _guessFilename(self, data, fname='', mimetype='', default=''):
        """
         Use the mimetype to guess the extension of the file/datafield if none exists.
         This is not a 100% correct, but does not really matter.
         In most cases it is nice that a word document has the doc extension, or that a picture has jpeg or bmp.
         It is a bit more human readable. When the extension is wrong it can just be ignored by the import anyway.
         """
        if not fname:
            return fname
        obj = self.obj
        mimetool = getToolByName(obj, 'mimetypes_registry')
        imimetype = mimetool.lookupExtension(fname)
        if mimetype and (imimetype is None): # no valid extension on fname
            # find extensions for mimetype
            classification = mimetool.classify(data, mimetype=mimetype)
            extensions = getattr(classification, 'extensions', default)
            extension = extensions[0] # just take the first one ... :-s
            fname = '%s.%s' % (fname, extension)
        return fname

class I18NLayerWrapper(ArchetypesWrapper):

    def __init__(self, obj):
        super(I18NLayerWrapper, self).__init__(obj)
        lang = obj.portal_properties.site_properties.default_language
        if lang not in obj.objectIds():
            print 'ERROR: Cannot get default data for I18NLayer "%s"' % self['_path']
        else:
            real = obj[lang]
            self['title'] = real.title.decode(self.charset, 'ignore')
            self['description'] = real.description.decode(self.charset, 'ignore')
            self['text'] = real.text.decode(self.charset, 'ignore')

        # Not lose information: generate properites es_title, en_title, etc.
        # TODO: Export all archetypes, but I don't need now, only document important fields
        for lang, content in obj.objectItems():
            data = dict(title = content.title,
                        description = content.description,
                        text = content.text)
            for field in data:
                self['_properties'].append(['%s_%s' % (lang, field),
                                            data[field].decode(self.charset, 'ignore'),
                                            'text'])


class ArticleWrapper(NewsItemWrapper):

    def __init__(self, obj):
        super(ArticleWrapper, self).__init__(obj)
        try:
            self['cooked_text'] = obj.cooked_text.decode(self.charset)
        except:
            self['cooked_text'] = obj.cooked_text.decode('latin-1')

        self['attachments_ids'] = obj.attachments_ids
        self['images_ids'] = obj.images_ids


class ZPhotoWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ZPhotoWrapper, self).__init__(obj)
        self['show_exif'] = obj.show_exif
        self['exif'] = obj.exif
        self['iptc'] = obj.iptc
        self['path'] = obj.path
        self['dir'] = obj.dir
        self['filename'] = obj.filename
        #self['_thumbs'] = obj._thumbs
        self['dict_info'] = obj.dict_info
        self['format'] = obj.format
        self['tmpdir'] = obj.tmpdir
        self['backup'] = obj.backup


class ZPhotoSlidesWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ZPhotoSlidesWrapper, self).__init__(obj)
        try:
            self['update_date'] = str(obj.update_date)
            self['show_postcard'] = obj.show_postcard
            self['show_ARpostcard'] = obj.show_ARpostcard
            self['show_rating'] = obj.show_rating
            self['size'] = obj.size
            self['max_size'] = obj.max_size
            self['sort_field'] = obj.sort_field
            self['allow_export'] = obj.allow_export
            self['show_export'] = obj.show_export
            #self['visits_log'] = obj.visits_log
            self['non_hidden_pic'] = obj.non_hidden_pic
            self['list_non_hidden_pic'] = obj.list_non_hidden_pic
            self['rows'] = obj.rows
            self['column'] = obj.column
            self['zphoto_header'] = obj.zphoto_header
            self['list_photo'] = obj.list_photo
            self['zphoto_footer'] = obj.zphoto_footer
            self['symbolic_photo'] = obj.symbolic_photo
            self['keywords'] = obj.keywords
            self['first_big'] = obj.first_big
            self['show_automatic_slide_show'] = obj.show_automatic_slide_show
            self['show_viewed'] = obj.show_viewed
            self['show_exif'] = obj.show_exif
            self['photo_space'] = obj.photo_space
            self['last_modif'] = str(obj.last_modif)
            self['show_iptc'] = obj.show_iptc
            self['formats_available'] = obj.formats_available
            self['default_photo_size'] = obj.default_photo_size
            self['formats'] = obj.formats
            self['actual_css'] = obj.actual_css
            self['thumb_width'] = obj.thumb_width
            self['thumb_height'] = obj.thumb_height
            #self['list_rating'] = obj.list_rating
            self['photo_folder'] = obj.photo_folder
            self['tmpdir'] = obj.tmpdir
            self['lib'] = obj.lib
            self['convert'] = obj.convert
            self['use_http_cache'] = obj.use_http_cache
        except Exception:
            import pdb; pdb.set_trace()


class LocalFSWrapper(BaseWrapper):

    def __init__(self, obj):
        super(LocalFSWrapper, self).__init__(obj)
        self['basepath'] = obj.basepath


class ZopeObjectWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ZopeObjectWrapper, self).__init__(obj)
        self['document_src'] = obj.document_src()
        # self['__datafields__'].append('document_src')

# TODO: should be also possible to set it with through parameters
CLASSNAME_TO_WAPPER_MAP = {
    'LargePloneFolder':         BaseWrapper,
    'Folder':                   BaseWrapper,
    'PloneSite':                BaseWrapper,
    'PloneFolder':              BaseWrapper,
    'Document':                 DocumentWrapper,
    'File':                     FileWrapper,
    'Image':                    ImageWrapper,
    'Link':                     LinkWrapper,
    'Event':                    EventWrapper,
    'NewsItem':                 NewsItemWrapper,
    'Favorite':                 LinkWrapper,
    'Topic':                    BaseWrapper,
    'ListCriterion':            ListCriteriaWrapper,
    'SimpleStringCriterion':    StringCriteriaWrapper,
    'SortCriterion':            SortCriteriaWrapper,
    'FriendlyDateCriterion':    DateCriteriaWrapper,

    # custom ones
    'I18NFolder':               I18NFolderWrapper,
    'I18NLayer':                I18NLayerWrapper,
    'PloneArticle':             ArticleWrapper,
    'ZPhotoSlides':             ZPhotoSlidesWrapper,
    'ZPhoto':                   ZPhotoWrapper,
    'PloneLocalFolderNG':       ArchetypesWrapper,
    'LocalFS':                  LocalFSWrapper,
    'ContentPanels':            BaseWrapper,
    'DTMLMethod':               ZopeObjectWrapper,
    'ZopePageTemplate':         ZopeObjectWrapper,

}
