import time
import string
import httplib
import urllib
import urllib2
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
        for option, default in self._options:
            setattr(self, option.replace('-', '_'),
                    self.get_option(option, default))

    def get_option(self, name, default):
        request = self.context.get('REQUEST', {})
        return request.get(name, self.options.get(name, default))

    def get_remote_item(self, path):
        remote_url = self.remote_url
        if not remote_url.endswith('/'):
            remote_url += '/'
        if path.startswith('/'):
            path = path[1:]
        return xmlrpclib.Server(
                urllib2.urlparse.urljoin(remote_url, urllib.quote(path)),
                BasicAuth(self.remote_username, self.remote_password),
                )

    def get_items(self, path, depth=0):
        if self.remote_crawl_depth == -1 or depth <= self.remote_crawl_depth:
            remote = self.get_remote_item(path)

            try:
                item = remote.get_item()
            except xmlrpclib.ProtocolError, e:
                self.logger.error(
                        'XML-RPC protocol error:\n'
                        '    URL: %s\n'
                        '    HTTP headers: %s\n'
                        '    %s: %s' %
                            (e.url, e.headers, e.errcode, e.errmsg))
                raise Exception('error1')

            if item.startswith('ERROR'):
                self.logger.error('%s :: EXPORT %s' % (path, item))
                raise Exception('error2')

            item = simplejson.loads(item)
            self.logger.info(':: Crawling %s' % item['_path'])
            yield item

            try:
                subitems = remote.get_children()
            except xmlrpclib.ProtocolError, e:
                self.logger.error(
                        'XML-RPC protocol error:\n'
                        '    URL: %s\n'
                        '    HTTP headers: %s\n'
                        '    %s: %s' %
                            (e.url, e.headers, e.errcode, e.errmsg))
                raise Exception('error3')

            if subitems.startswith('ERROR'):
                self.logger.error('%s :: \n%s' % (path, item))
                raise Exception('error4')

            for subitem_id in simplejson.loads(subitems):
                subitem_path = path + '/' + subitem_id

                if subitem_path[len(self.remote_path):] in self.skip_remote_path:
                    logger.info(':: Skipping -> ' + subitem_path)
                    continue

                for subitem in self.get_items(subitem_path, depth+1):
                    yield subitem

    def __iter__(self):
        for item in self.previous:
            yield item

        for item in self.get_items(self.remote_path):
            if item:
                yield item
