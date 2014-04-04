from django.conf.urls import *
from django.contrib.syndication.views import feed

from timelines.views import *
from timelines.feeds import *

urlpatterns = patterns('',
    url(
        regex = "^$",
        view  = archive,
        name  = "timelines_archive_user",
    ),
    url(
        regex = "^today/$",
        view  = today,
        name  = "timelines_today_user",
    ),
    url(
        regex = "^(?P<year>\d{4})/$",
        view  = year,
        name  = "timelines_year_user",
    ),
    url(
        regex = "^(?P<year>\d{4})/(?P<month>\w{3})/$",
        view  = month,
        name  = "timelines_month_user",
    ),
    url(
        regex = "^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/$",
        view  = day,
        name  = "timelines_day_user",
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