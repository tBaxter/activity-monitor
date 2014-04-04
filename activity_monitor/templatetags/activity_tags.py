import datetime
import dateutil.parser

from django import template
from django.contrib.contenttypes.models import ContentType
from django.template import resolve_variable

from activity_monitor.models import Activity


register = template.Library()


@register.inclusion_tag('activity_monitor/inclusion/recent_activity.html')
def show_recent_activity(count=10, detailed=''):
    """
    Simple inclusion tag to drop in recent events.
    If detailed is set, will also return the newest 4 members
    Usage:
    {% show_recent_activity %}
    Or, to set count:
    {% show_recent_activity 6 %}
    Or to send detailed version:
    {% show_recent_activity 8 detailed %}
    """
    user_list = []
    activities = Activity.objects.all().order_by('-timestamp')
    if detailed:
        user_ct = ContentType.objects.get(app_label='auth', model='user')
        user_list = activities.filter(content_type=user_ct)[:5]
        activities = activities.exclude(content_type=user_ct)
    activities = activities[:count]

    # come up with some default activity strings
    for act in activities:
        return {'activities': activities, 'user_list': user_list}


@register.tag
def get_activities(parser, token):
    """
    Super-customizable tag.
    Loads Activity Monitor 'Activity' objects into the context.
    In the simplest mode, the most recent N items will be returned.
    Activity objects must be limited in some way; you must either pass `limit` or `between`.
    ::
    Example, fetching 10 most recent items:
    {% get_activities limit 10 as items %}

    Defaults to newest items first, unless you reverse:
    {% get_activities limit 10 reversed as items %}

    Can fetch between two given dates:
    {% get_activities between "2007-01-01" and "2007-01-31" as items %}

    Dates can be in any format understood by ``dateutil.parser``, and can be variables.

    Dates can also be the magic strings "now" or "today":
    {% get_activities between "2007-01-01" and "today" as items %}

    Can limit items by type:
    {% get_activities oftype video oftype photo limit 10 as items %}
    -- `oftype`` can be given as many times as you like;
    --  only those types will be returned.
    -- The arguments to ``oftype`` are the lowercase class names of monitored items.

    Or can exclude types using ``excludetype``::
    {% get_timeline_items excludetype video limit 10 as items %}

    You can not use both ``oftype`` and ``excludetype`` in the same tag invocation.

    You can also get items for a user:
    {% get_activities limit 10 as items foruser <user> %}
    """

    # Parse out the arguments
    bits = token.split_contents()
    tagname = bits[0]
    bits = iter(bits[1:])
    args = {}
    for bit in bits:
        try:
            if bit == "limit":
                try:
                    args["limit"] = int(bits.next())
                except ValueError:
                    raise template.TemplateSyntaxError("%r tag: 'limit' requires an integer argument" % tagname)
            elif bit == "between":
                args["start"] = bits.next()
                and_ = bits.next()
                args["end"] = bits.next()
                if and_ != "and":
                    raise template.TemplateSyntaxError("%r tag: expected 'and' in 'between' clause, but got %r" % (tagname, and_))
            elif bit == "oftype":
                args.setdefault("oftypes", []).append(bits.next())
            elif bit == "excludetype":
                args.setdefault("excludetypes", []).append(bits.next())
            elif bit == "reversed":
                args["reversed"] = True
            elif bit == "as":
                args["asvar"] = bits.next()
            elif bit == "foruser":
                args["foruser"] = bits.next()
            else:
                raise template.TemplateSyntaxError("%r tag: unknown argument: %r" % (tagname, bit))
        except StopIteration:
            raise template.TemplateSyntaxError("%r tag: an out of arguments when parsing %r clause" % (tagname, bit))

    # Make sure "as" was given
    if "asvar" not in args:
        raise template.TemplateSyntaxError("%r tag: missing 'as'" % tagname)

    # Either "limit" or "between" has to be specified
    if "limit" not in args and ("start" not in args or "end" not in args):
        raise template.TemplateSyntaxError("%r tag: 'limit' or a full 'between' clause is required" % tagname)

    # It's an error to have both "oftype" and "excludetype"
    if "oftype" in args and "excludetype" in args:
        raise template.TemplateSyntaxError("%r tag: can't handle both 'oftype' and 'excludetype'" % tagname)

    # Each of the "oftype" and "excludetype" arguments has be a valid model
    for arg in ("oftypes", "excludetypes"):
        if arg in args:
            model_list = []
            for name in args[arg]:
                try:
                    model_list.append(Activity.objects.models_by_name[name])
                except KeyError:
                    raise template.TemplateSyntaxError("%r tag: invalid model name: %r" % (tagname, name))
            args[arg] = model_list

    return GetAggregateActivitiesNode(**args)


class GetAggregateActivitiesNode(template.Node):
    def __init__(self, asvar, foruser=None, limit=None, start=None, end=None, oftypes=[], excludetypes=[], reversed=False):
        self.asvar   = asvar
        self.foruser = foruser
        self.limit   = limit
        self.start   = start
        self.end     = end
        self.oftypes = oftypes
        self.excludetypes = excludetypes
        self.reversed = reversed

    def render(self, context):
        qs = Activity.objects.all()

        # Handle user if given
        if self.foruser:
            user = resolve_variable(self.foruser, context)
            qs = qs.filter(user=user)

        # Handle start/end dates if given
        if self.start:
            start = self.resolve_date(self.start, context)
            end   = self.resolve_date(self.end, context)
            if start is None or end is None:
                return ""
            qs = qs.filter(timestamp__range=(start, end))

        # Handle types
        CT = ContentType.objects.get_for_model
        if self.oftypes:
            qs = qs.filter(content_type__id__in=[CT(m).id for m in self.oftypes])
            if self.excludetypes:
                qs = qs.exclude(content_type__id__in=[CT(m).id for m in self.excludetypes])

        # Handle reversed
        if self.reversed:
            qs = qs.order_by("timestamp")
        else:
            qs = qs.order_by("-timestamp")

        # Handle limit
        if self.limit:
            qs = qs[:self.limit]

        # Set the context
        context[self.asvar] = list(qs)
        return ""

    def resolve_date(self, d, context):
        """Resolve start/end, handling literals"""
        try:
            d = template.resolve_variable(d, context)
        except template.VariableDoesNotExist:
            return None

        # Handle date objects
        if isinstance(d, (datetime.date, datetime.datetime)):
            return d

        # Assume literals or strings
        if d == "now":
            return datetime.datetime.now()
        if d == "today":
            return datetime.date.today()
        try:
            return dateutil.parser.parse(d)
        except ValueError:
            return None
