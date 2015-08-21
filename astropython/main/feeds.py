from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed,Rss201rev2Feed

from .utilities import get_all_native_objects

"""
REPLACE HARDCODED URLS TO ASTROPYTHON.ORG
"""
class RSSFeed(Feed):
    feed_type=Rss201rev2Feed
    title = "Latest Posts on Astropython.org - Python for Astronomers"
    link = "http://www.astropython.org/feeds/rss"
    description = "This feed hosts all the posts posted on Astrpython.org"

    def items(self):
        return get_all_native_objects('all')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        body=item.body
        body=body.replace("&gt",'>')
        body=body.replace("&lt",'<')

    def item_link(self,item):
        return 'http://www.astropython.org'+item.get_absolute_url()

    def item_author_name(self,item):
        authors=''
        for author in item.authors.all():
            authors+=str(author)+','
        return authors[:-1]

    def item_author_email(self,item):
        authors=''
        for author in item.authors.all():
            authors+=str(author.email)+','
        return authors[:-1]

    def item_pubdate(self, item):
        return item.created

    def item_updateddate(self, item):
        return item.updated


class ATOMFeed(RSSFeed):
    feed_type = Atom1Feed
    subtitle = RSSFeed.description