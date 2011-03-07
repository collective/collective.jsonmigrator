import time
import string
import httplib
import urllib2
import xmlrpclib
import simplejson
from base64 import encodestring
from zope.interface import implements
from zope.interface import classProvides
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.jsonmigrator import logger


class BasicAuth(xmlrpclib.Transport):

    def __init__(self, username=None, password=None, verbose=False):
        self.username = username
        self.password = password
        self.verbose = verbose
        self._use_datetime = True

    def request(self, host, handler, request_body, verbose):
        h = httplib.HTTP(host)

        h.putrequest("POST", handler)
        h.putheader("Host", host)
        h.putheader("User-Agent", self.user_agent)
        h.putheader("Content-Type", "text/xml")
        h.putheader("Content-Length", str(len(request_body)))

        if self.username is not None and self.password is not None:
            h.putheader("AUTHORIZATION", "Basic %s" % string.replace(
                    encodestring("%s:%s" % (self.username, self.password)),
                    "\012", ""))
        h.endheaders()

        if request_body:
            h.send(request_body)

        errcode, errmsg, headers = h.getreply()

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        return self.parse_response(h.getfile())


class DefaultPathConverter(object):

    def to_local(self, path):
        return path

    def to_remote(self, path):
        return path


class RemoteSource(object):
    """ """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.name, self.options = name, options
        self.transmogrifier, self.previous = transmogrifier, previous
        self.context = transmogrifier.context

        self.start_time = time.time()
        self.logger = logger
        registry = getUtility(IRegistry)
        self.remote_url = 'http://192.168.1.55:8080/Plone'
#                registry.get('collective.jsonmigrator.remoteurl')
        self.remote_username ='admin'
#                registry.get('collective.jsonmigrator.username')
        self.remote_password = 'admin'
#                registry.get('collective.jsonmigrator.password')
        self.portal = getUtility(ISiteRoot)
        self.portal_path = '/'.join(self.portal.getPhysicalPath())
        self.max_depth = int(self.options.get('depth', -1))

        start_path = self.options.get('start_path', None)
        if start_path is not None:
            self.start_path = start_path
        elif self.context.getId() == 'portal_setup':
            self.start_path = '/'.join(self.portal.getPhysicalPath())
        else:
            self.start_path = '/'.join(self.context.getPhysicalPath())

        # TODO: need to implement "path-converter" resolving
        self.path_converter = DefaultPathConverter()

        # SKIP OPTIONS
        self.skip = {}
        for option in self.options.keys():
            if option.startswith('skip_'):
                self.skip[option[5:]] = self.options[option].split()

    def __iter__(self):
        for item in self.previous:
            yield item

        remote_path = self.path_converter.to_remote(self.start_path)
        i = 1
        for item in self.get_items(remote_path):
            self.logger.info('%s - %s' % (i, item['_remote_path']))
            i += 1
            #yield item

    def get_items(self, path, depth=0):
        if self.max_depth == -1 or depth <= self.max_depth:
            remote_item = self.remote_item(path)

            try:
                item = remote_item.get_item()
            except xmlrpclib.ProtocolError, e:
                self.logger.error('XML-RPC protocol error:\n'
                                  '    URL: %s\n'
                                  '    HTTP headers: %s\n'
                                  '    %s: %s' %
                                  (e.url, e.headers, e.errcode, e.errmsg))
                import ipdb; ipdb.set_trace()
                return
            except:
                import ipdb; ipdb.set_trace()
                return
            try:
                if item.startswith('ERROR'):
                    self.logger.error('%s :: EXPORT %s' % (path, item))
                    import ipdb; ipdb.set_trace()
                    return
            except:
                import ipdb; ipdb.set_trace()
                return

            item = simplejson.loads(item)
            item['_remote_path'] = item['_path']
            item['_path'] = self.path_converter.to_local(item['_remote_path'])

            # TODO: SKIP / INCLUDE rules

            yield item
            # TODO: we should check if item is created if not then add it to waiting list
            # and continue only if item successfully created

            try:
                subitems = remote_item.get_children()
            except xmlrpclib.ProtocolError, e:
                self.logger.error('XML-RPC protocol error:\n'
                                  '    URL: %s\n'
                                  '    HTTP headers: %s\n'
                                  '    %s: %s' %
                                  (e.url, e.headers, e.errcode, e.errmsg))
                import ipdb; ipdb.set_trace()
                return
            except:
                import ipdb; ipdb.set_trace()
                return

            if subitems.startswith('ERROR'):
                self.logger.error('%s :: \n%s' % (path, item))
                import ipdb; ipdb.set_trace()
                return

            for subitem_id in simplejson.loads(subitems):
                subitem_path = path+'/'+subitem_id
                if subitem_path in self.skip.get('_remote_path', []):
                    logger.info('SKIPPING -> ' + subitem_path)
                    continue
                for subitem in self.get_items(subitem_path, depth+1):
                    yield subitem

    def remote_item(self, path):
        remote_url = self.remote_url
        if not remote_url.endswith('/'):
            remote_url += '/'
        if path.startswith('/'):
            path = path[1:]
        return xmlrpclib.Server(
                urllib2.urlparse.urljoin(remote_url, path),
                BasicAuth(self.remote_username, self.remote_password),
                )


        '''
        tmp = self.server.get_children()
        paths = self.options['remote_paths']
        base_depth = len(paths[0].split('/'))
        plname = self.options['plname']

        for path in paths:
            self.logger.warn('Importing %s ...' % path)
            try:
                item = self.server.export_json_item(path)
            except xmlrpclib.ProtocolError, e:
                self.logger.error('XML-RPC protocol error:\n'
                                  '    URL: %s\n'
                                  '    HTTP headers: %s\n'
                                  '    %s: %s' %
                                  (e.url, e.headers, e.errcode, e.errmsg))
                continue
            if item.startswith('ERROR'):
                self.logger.error('%s :: EXPORT %s' % (path, item))
                continue
            item = simplejson.loads(item)
            skip_item = True
            try:
                obj, local_path = self.get_object(item, path)
            except KeyError:
                skip_item = False
            except AttributeError:
                self.logger.warn('    Importing new object for %s' % path)
                skip_item = False
            else:
                try:
                    local_md = DateTime(obj.ModificationDate())
                    remote_md = DateTime(self.server.get_modification_date(path))
                    migration_date = get_import_date(obj, plname)
                except Exception, e:
                    self.logger.error('Error obtaining dates for %s: %s' % path)
                else:
                    if local_md == migration_date:
                        self.logger.warn('    Reimporting %s,'
                                         ' local md == migration date implies'
                                         ' an error in migration' % path)
                        skip_item == False
                    elif remote_md > migration_date and local_md < migration_date:
                        self.logger.warn('    Reimporting %s: no local modifications'
                                         ' and remote modifications' % path)
                        skip_item = False
                    elif local_md > migration_date and remote_md > migration_date:
                        if eval(self.options['reimport_changed_both']):
                            self.logger.warn('    Reimporting %s: local modifications'
                                             ' and remote modifications' % path)
                            skip_item = False
                    elif local_md > migration_date and skip_item and \
                            eval(self.options['reimport_changed_lo']):
                        self.logger.warn('    Reimporting %s: local modifications'
                                          ' and not remote modifications' % path)
                        skip_item = False
                    elif local_md == remote_md and skip_item and \
                            eval(self.options['reimport_unchanged']):
                        self.logger.warn('    Reimporting %s: object unchanged'
                                          ' locally and remotelly since last'
                                          ' migration date' % path)
                        skip_item = False
                    else:
                        self.logger.warn('    NOT importing %s: local md: %s'
                                ' -- remote md: %s -- last migration: %s'
                                 % (path, local_md, remote_md, migration_date))
            if not skip_item:
                yield item
                try:
                    obj, local_path = self.get_object(item, path)
                except KeyError:
                    self.logger.error('IMPORT ERROR :: no pathkey in item %s' % path)
                except AttributeError:
                    self.logger.error('IMPORT ERROR :: %s -> %s' %
                                                (path, local_path))
                else:
                    try:
                        anno = IAnnotations(obj)
                    except TypeError:
                        pass
                    else:
                        if 'collective.sync_migrator' not in anno:
                            anno['collective.sync_migrator'] = PersistentDict()
                        anno['collective.sync_migrator'][plname] = DateTime()
                    self.logger.warn('DONE')
            if int(max_depth) == -1:
                new_paths = self.server.list_item_children(path)
                new_paths = simplejson.loads(new_paths)
                new_paths = ['%s/%s' % (path, p) for p in new_paths]
                paths += new_paths
            else:
                current_depth = len(path.split('/'))
                relative_depth = current_depth - base_depth
                if max_depth > relative_depth:
                    new_paths = self.server.list_item_children(path)
                    new_paths = simplejson.loads(new_paths)
                    new_paths = ['%s/%s' % (path, p) for p in new_paths]
                    paths += new_paths
        t = time.time() - self.start_time
        self.logger.footer(int(t))

    def get_object(self, item, path):
        pathkey = self.pathkey(*item.keys())[0]
        if not pathkey:                     # not enough info
            try:
                obj = self.context.unrestrictedTraverse(path)
            except Exception, e:
                raise KeyError("Path key not found for object on %s" % path)
            else:
                return obj, path
        local_path = item[pathkey]
        try:
            obj = self.context.unrestrictedTraverse(local_path)
        except Exception, e:
            raise AttributeError("Object not found in %s" % local_path)
        return obj, local_path'''
