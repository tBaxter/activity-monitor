from django.conf.urls import *
from django.contrib.syndication.views import feed

from activity_monitor.views import *
from activity_monitor.feeds import *

urlpatterns = patterns('',
    url(
        regex = "^$",
        view  = archive,
        name  = "timelines_archive",
    ),
    url(
        regex = "^today/$",
        view  = today,
        name  = "timelines_today",
    ),
    url(
        regex = "^(?P<year>\d{4})/$",
        view  = year,
        name  = "timelines_year",
    ),
    url(
        regex = "^(?P<year>\d{4})/(?P<month>\w{3})/$",
        view  = month,
        name  = "timelines_month",
    ),
    url(
        regex = "^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/$",
        view  = day,
        name  = "timelines_day",
    ),
)

# URLs for feeds...

# feeds = {
#   'latest-items': LatestItems,
# }
# 
# 
# urlpatterns += patterns('',
#   url(
#     regex   = '^feeds/(?P<url>.*)/$',
#     view    = feed,
#     kwargs  = { 'feed_dict': feeds },
#     name    = 'timelines_feeds',
#   )
# )