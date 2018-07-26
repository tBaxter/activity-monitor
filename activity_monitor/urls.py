from django.urls import path, re_path

from .views import action_list, actions_for_period, actions_for_today

urlpatterns = [
    path('', actions_for_today, name="actions_for_today"),
    re_path(r"^(?P<year>\d{4})/$", actions_for_period, name="actions_for_year",),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/$",
        actions_for_period,
        name="actions_for_month",
    ),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$",
        actions_for_period,
        name="actions_for_day",
    ),
    path('archive/', action_list, name="action_archive"),
    path('archive/<slug:username>/', action_list, name="action_archive_for_user"),
]
