import time
import string
import httplib
import urllib
import urllib2
import urlparse
import xmlrpclib
import simplejson
from base64 import encodestring
from zope.interface import implements
from zope.interface import classProvides
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

class Urllibrpc(object):
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def __getattr__(self, item):
        def callable():
            scheme,netloc,path,params,query,fragment = urlparse.urlparse(self.url)
            if '@' not in netloc:
                netloc = '%s:%s@%s'%(self.username, self.password, netloc)
            if path.endswith("/"):
                path = path[:-1]
            path = path + '/' + item
            url = urlparse.urlunparse( (scheme,netloc,path,params,query,fragment) )
            f = urllib.urlopen(url)
            content = f.read()
            if f.getcode() != 200:
                raise Exception(content)
            f.close()
            return content
        return callable
        

class RemoteSource(object):
    """ """

    name = 'collective.jsonmigrator.remotesource'
    _options = [
            ('remote-url', 'http://127.0.0.1:8080/Plone'),
            ('remote-username', 'admin'),
            ('remote-password', 'admin'),
            ('remote-path', '/Plone'),
            ('remote-crawl-depth', -1),
            ('remote-skip-path', ''),
            ]

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.name, self.options, self.previous = name, options, previous
        self.transmogrifier = transmogrifier
        self.context = transmogrifier.context
        self.logger = logger
        for option, default in self._options:
            setattr(self, option.replace('-', '_'),
                    self.get_option(option, default))

    def get_option(self, name, default):
        request = self.context.get('REQUEST', {})
        return request.get(
                    'form.widgets.'+name.replace('-', '_'),
                    self.options.get(name, default))

    def get_remote_item(self, path):
        remote_url = self.remote_url+self.remote_path
        if not remote_url.endswith('/'):
            remote_url += '/'
        if path.startswith('/'):
            path = path[1:]
        url = urllib2.urlparse.urljoin(remote_url, urllib.quote(path))
        #return xmlrpclib.Server(
        #        url,
        #        BasicAuth(self.remote_username, self.remote_password),
        #        )
        return Urllibrpc(url, self.remote_username, self.remote_password)


    def get_items(self, path, depth=0):
        if self.remote_crawl_depth == -1 or depth <= self.remote_crawl_depth:
            self.logger.info(':: Crawling %s' % path)
            remote = self.get_remote_item(path)
            item = None

            try:
                item = remote.get_item()
            except xmlrpclib.ProtocolError, e:
                logger.error(
                        'XML-RPC protocol error:\n'
                        '    URL: %s\n'
                        '    HTTP headers: %s\n'
                        '    %s: %s' %
                            (e.url, e.headers, e.errcode, e.errmsg))
                raise Exception('error1')
            except Exception, e:
                import ipdb; ipdb.set_trace()

            if item.startswith('ERROR'):
                logger.error('%s :: EXPORT %s' % (path, item))
                # Item could be portal object that has children but we can't import
                # Keep going and assume we have container already to put this content in
                #raise Exception('error2')
            elif item is not None:
                try:
                    item = simplejson.loads(item)
                except:
                    import ipdb; ipdb.set_trace()
                import ipdb; ipdb.set_trace()
                yield item

            try:
                subitems = remote.get_children()
            except xmlrpclib.ProtocolError, e:
                logger.error(
                        'XML-RPC protocol error:\n'
                        '    URL: %s\n'
                        '    HTTP headers: %s\n'
                        '    %s: %s' %
                            (e.url, e.headers, e.errcode, e.errmsg))
                raise Exception('error3')

            if subitems.startswith('ERROR'):
                logger.error('%s :: \n%s' % (path, item))
                raise Exception('error4')

            for subitem_id in simplejson.loads(subitems):
                subitem_path = path + '/' + subitem_id

                if subitem_path[len(self.remote_path):] in self.remote_skip_path:
                    logger.info(':: Skipping -> ' + subitem_path)
                    continue

                for subitem in self.get_items(subitem_path, depth+1):
                    yield subitem

    def __iter__(self):
        for item in self.previous:
            yield item
        if self.remote_path.startswith("/"):
            self.remote_path = self.remote_path[1:]

        for item in self.get_items(self.remote_path):
            if item:
                yield item
