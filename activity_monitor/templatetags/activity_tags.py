import datetime

from django import template
from django.template import loader, Context

from activity_monitor.models import Activity
from activity_monitor.utils import group_activities


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
    value = [str(item) for item in value]

    if len(value) == 1:
        return value[0]
    if len(value) == 2:
        return "%s and %s" % (value[0], value[1])

    # join all but the last element
    all_but_last = ", ".join(value[:-1])
    return "%s and %s" % (all_but_last, value[-1])


@register.simple_tag
def render_activity(activity, grouped_activity=None, *args, **kwargs):
    """
    Given an activity, will attempt to render the matching template snippet
    for that activity's content object
    or will return a simple representation of the activity.

    Also takes an optional 'grouped_activity' argument that would match up with
    what is produced by utils.group_activity
    """
    template_name = 'activity_monitor/includes/models/{0.app_label}_{0.model}.html'.format(activity.content_type)
    try:
        tmpl = loader.get_template(template_name)
    except template.TemplateDoesNotExist:
        return None
    # we know we have a template, so render it
    content_object = activity.content_object
    return tmpl.render(Context({
        'activity': activity,
        'obj': content_object,
        'grouped_activity': grouped_activity
    }))


@register.simple_tag
def show_activity_count(date=None):
    """
    Simple filter to get activity count for a given day.
    Defaults to today.
    """
    if not date:
        today = datetime.datetime.now() - datetime.timedelta(hours = 24)
        return Activity.objects.filter(timestamp__gte=today).count()
    return Activity.objects.filter(timestamp__gte=date).count()


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


@register.inclusion_tag('activity_monitor/includes/activity_wrapper.html')
def show_new_activity(last_seen=None, cap=1000, template='grouped', include=None, exclude=None):
    """
    Inclusion tag to show new activity,
    either since user was last seen or today (if not last_seen).

    Note that passing in last_seen is up to you.

    Usage: {% show_new_activity %}
    Or, to show since last seen: {% show_new_activity last_seen %}

    Can also cap the number of items returned. Default is 1000.

    Usage: {% show_new_activity last_seen 50 %}

    Allows passing template, controlling level of detail.
    Template choices are:
    * 'plain': simple list
    * 'grouped': items are grouped by content type
    * 'detailed': items are grouped and can use custom template snippets

    Usage: {% show_new_activity last_seen 50 'plain' %}

    If no template choice argument is passed, 'grouped' will be used.

    Also accepts "include" and "exclude" options to control which activities are returned.
    Content types should be passed in by name.

    * 'include' will **only** return passed content types
    * 'exclude' will **not** return passed content types

    Include is evaluated before exclude.

    Usage: {% show_new_activity last_seen 50 'plain' exclude="comment,post" %}

    """
    if not last_seen or last_seen is '':
        last_seen = datetime.date.today()
    actions = Activity.objects.filter(timestamp__gte=last_seen)

    if include:
        include_types = include.split(',')
        actions = actions.filter(content_type__model__in=include_types)

    if exclude:
        exclude_types = exclude.split(',')
        actions = actions.exclude(content_type__model__in=exclude_types)

    # Now apply cap
    actions = actions[:cap]

    if template=='detailed':
        template = 'activity_monitor/includes/detailed.html'
        actions = group_activities(actions)
    elif template=='grouped':
        template = 'activity_monitor/includes/grouped_list.html'
        actions = group_activities(actions)
    else:
        template = 'activity_monitor/includes/activity_list.html'


    return {'actions': actions, 'selected_template': template}

@register.inclusion_tag('activity_monitor/includes/paginate_by_day.html')
def paginate_activity(visible_date=None):
    """
    Creates "get previous day" / "get next day" pagination for activities.

    Visible date is the date of the activities currently being shown,
    represented by a date object.

    If not provided, it will default to today.

    #Expects date as default "Aug. 25, 2014" format.
    """
    #if visible_date:
    #    visible_date = datetime.datetime.strptime(visible_date, "%b %d ")

    if not visible_date:
        visible_date = datetime.date.today()
    previous_day = visible_date - datetime.timedelta(days=1)
    if visible_date == datetime.date.today():
        next_day = None
    else:
        next_day = visible_date + datetime.timedelta(days=1)
    return {'previous_day': previous_day, 'next_day': next_day}

