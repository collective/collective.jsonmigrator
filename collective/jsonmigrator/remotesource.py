import time
import logging

from zope.interface import implements
from zope.interface import classProvides
from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint

import string
import httplib
import xmlrpclib
from base64 import encodestring


class BasicAuth(xmlrpclib.Transport):

    def __init__(self, username=None, password=None):
        self.username=username
        self.password=password
        self._use_datetime = True

    def request(self, host, handler, request_body):
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


def RemoteServer(remoteurl, username, password):
    return xmlrpclib.Server(
            remoteurl,
            BasicAuth(username, password),
            )


class RemoteSource(object):
    """ """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.name, self.options = name, options
        self.transmogrifier, self.previous = transmogrifier, previous
        self.context = transmogrifier.context
        registry = getUtility(IRegistry)

        self.start_time = time.time()
        self.logger = logging.getLogger('collective.blueprint.jsonmigrator')
        self.server = RemoteServer(
                registry.get('collective.blueprint.jsonmigrator.remoteurl'),
                registry.get('collective.blueprint.jsonmigrator.username'),
                registry.get('collective.blueprint.jsonmigrator.password'),
                )

        self.max_depth = int(self.options['depth'])

    def __iter__(self):

        for item in self.previous:
            yield item


        import ipdb; ipdb.set_trace()
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
        return obj, local_path

