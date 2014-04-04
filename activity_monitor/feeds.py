from django.conf import settings
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.contrib.sites.models import Site

from activity_monitor.models import Activity

UserModel = getattr(settings, "AUTH_USER_MODEL", "auth.User")

site = Site.objects.get(id=settings.SITE_ID)
site_url = "http://%s/" % site.domain


class LatestUserTimelineItems(Feed):
    """ A feed of the latest UserTimelineItem objects added to the site. """

    title_template = 'timelines/feeds/item_title.html'
    description_template = 'timelines/feeds/item_description.html'

    title = "%s: Newest timeline items" % site.name
    link = site_url
    description = "The latest timeline items added at %s" % site.name

    def items(self):
        return Activity.objects.all().order_by('-timestamp')[:15]

    def item_pubdate(self, item):
        return item.timestamp

    def item_author_name(self, item):
        return item.user.encode("utf-8")

    item_author_email = ""

    def item_link(self, item):
        try:
            return item.get_absolute_url()
        except:
            return ""

    def item_author_link(self, item):
        return item.user.get_absolute_url()


class LatestUserTimelineItemsPerUser(Feed):
    """ A feed of the latest UserTimelineItem objects added to the site by a particular user. """

    title_template = 'timelines/feeds/item_title.html'
    description_template = 'timelines/feeds/item_description.html'

    link = site_url
    description = "The latest timeline items added at %s" % site.name

    def get_object(self, bits):
        username = bits[0]
        try:
            return UserModel.objects.get(username=username)
        except ValueError:
            raise FeedDoesNotExist

    def title(self, obj):
        return "%s: Activity for %s" % (site.name, obj.preferred_name.encode("utf-8"))

    def items(self, obj):
        return Activity.objects.filter(user=obj)[:15]

    def item_pubdate(self, item):
        return item.timestamp

    def item_author_name(self, item):
        return item.user.preferred_name.encode("utf-8")

    def item_link(self, item):
        try:
            return item.get_absolute_url()
        except:
            return ""

    def item_author_email(self, item):
        return item.user.email

    def item_author_link(self, item):
        return item.user.get_absolute_url()
