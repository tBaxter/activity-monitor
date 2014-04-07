from django.conf.urls import patterns, url

from activity_monitor.views import action_list, actions_for_period, actions_for_today

urlpatterns = patterns('',
    url(
        regex = "^$",
        view  = actions_for_today,
        name  = "actions_for_today",
    ),
    url(
        regex = "^(?P<year>\d{4})/$",
        view  = actions_for_period,
        name  = "actions_for_year",
    ),
    url(
        regex = "^(?P<year>\d{4})/(?P<month>\d{2})/$",
        view  = actions_for_period,
        name  = "actions_for_month",
    ),
    url(
        regex = "^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$",
        view  = actions_for_period,
        name  = "actions_for_day",
    ),
    url(
        regex = "^archive/$",
        view  = action_list,
        name  = "action_archive",
    ),
    url(
        regex = "^archive/(?P<username>[-\w]+)/$",
        view  = action_list,
        name  = "action_archive_for_user",
    ),
)
