import datetime
import dateutil.parser

from django import template
from django.contrib.contenttypes.models import ContentType
from django.template import resolve_variable

from activity_monitor.models import Activity


register = template.Library()


@register.filter
def join_and(value):
    """Given a list of strings, format them with commas and spaces, but
    with 'and' at the end.

    >>> join_and(['apples', 'oranges', 'pears'])
    "apples, oranges, and pears"

    There is surely a better home for this

    """
    # convert numbers to strings
    value = [unicode(item) for item in value]

    if len(value) == 1:
        return value[0]
    if len(value) == 2:
        return "%s and %s" % (value[0], value[1])

    # join all but the last element
    all_but_last = ", ".join(value[:-1])
    return "%s and %s" % (all_but_last, value[-1])




@register.inclusion_tag('activity_monitor/includes/activity_list.html')
def show_activity(count=10):
    """
    Simple inclusion tag to drop in recent activities.
    Shows 10 by default
    Usage:
    {% show_recent_activity %}
    Or, to set count:
    {% show_recent_activity 6 %}
   """
    activities =  Activity.objects.all().order_by('-timestamp')[:count]

    return {'activities': activities}


@register.inclusion_tag('activity_monitor/includes/activity_list.html')
def show_new_activity(last_seen=None, cap=1000):
    """
    Simple inclusion tag to show new activity, 
    either since user last seen or today.
    Usage:
    {% show_new_activity %}
    
    or, to show since last seen:
    {% show_new_activity last_seen %}
    Note that passing in last_seen is up to you.

    You can also cap the number of items returned:
    {% show_new_activity last_seen 50 %}

    """
    if not last_seen:
        last_seen = datetime.date.today()
    activities = Activity.objects.filter(timestamp__gte=last_seen)[:cap]
    
    return {'activities': activities}
