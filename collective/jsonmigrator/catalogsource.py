import base64
import urllib
import urllib2
import simplejson
from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.jsonmigrator import logger

class CatalogSourceSection(object):
    """A source section which creates items from a remote Plone site by
       querying it's catalog.
    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.options = options
        self.context = transmogrifier.context

        self.remote_url = self.get_option('remote-url', 
                                          'http://localhost:8080')
        remote_username = self.get_option('remote-username', 'admin')
        remote_password = self.get_option('remote-password', 'admin')

        catalog_path = self.get_option('catalog-path', '/Plone/portal_catalog')
        self.site_path_length = len('/'.join(catalog_path.split('/')[:-1]))

        catalog_query = self.get_option('catalog-query', None)
        catalog_query = ' '.join(catalog_query.split())
        catalog_query = base64.b64encode(catalog_query)

        # Install a basic auth handler
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='Zope',
                                  uri=self.remote_url,
                                  user=remote_username,
                                  passwd=remote_password)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)

        req = urllib2.Request('%s%s/get_catalog_results' % (self.remote_url,
            catalog_path), urllib.urlencode({'catalog_query': catalog_query}))
        try:
            f = urllib2.urlopen(req)
            resp = f.read()
        except urllib2.URLError:
            raise

        self.item_paths = sorted(simplejson.loads(resp))

    def get_option(self, name, default):
        """Get an option from the request if available and fallback to the
        transmogrifier config.
        """
        request = self.context.get('REQUEST', {})
        value = request.form.get('form.widgets.'+name.replace('-', '_'),
                                 self.options.get(name, default))
        if isinstance(value, unicode):
            value = value.encode('utf8')
        return value

    def __iter__(self):
        for item in self.previous:
            yield item
        
        for path in self.item_paths:
            item = self.get_remote_item(path)
            if item:
                item['_path'] = item['_path'][self.site_path_length:]
                yield item

    def get_remote_item(self, path):
        item_url = '%s%s/get_item' % (self.remote_url, path)
        try:
            f = urllib2.urlopen(item_url)
            item_json = f.read()
        except urllib2.URLError, e:
            logger.error("Failed reading item from %s. %s" (item_url, str(e)))
            return None
        item = simplejson.loads(item_json)
        return item
