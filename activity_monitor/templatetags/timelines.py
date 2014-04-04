import datetime
import dateutil.parser
from django import template
from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.template import resolve_variable

UserTimelineItem = models.get_model("timelines", "usertimelineitem")

register = template.Library()

class GetLatestByModelsNode(template.Node):
    def __init__(self, num, model_string, varname):
      self.num, self.model_string, self.varname  = num, model_string, varname

    def render(self, context):
      from timelines.views import *
      try:
        model_string_list = self.model_string.split(',')
        queryset, content_types = filter_queryset_by_model_list(UserTimelineItem.objects.all().order_by("-timestamp").select_related(depth=1), model_string_list)
        if int(self.num) == 1:
          context[self.varname] = queryset[0]
        else:
          context[self.varname] = queryset[:int(self.num)]
      except:
        pass
      return ''


@register.tag
def get_latest_from_models(parser, token):
    """
    Gets the latest [num] UserTimelineItem objects from the timelines models, such as for use in a mini-tumblelog.
    If [num] is 1, returns a single UserTimelineItem. Otherwise, returns a QuerySet.
    Example::

        {% get_latest_from_models 10 "media.photo,statuses.status" as tumblelog %}

    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'%s' tag takes four arguments" % bits[0])
    if bits [3] != 'as':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    
    
    return GetLatestByModelsNode(bits[1], bits[2], bits[4])
    
    
@register.tag
def get_timeline_items(parser, token):
    """
    Load timelines ``UserTimelineItem`` objects into the context.In the simplest mode, the
    most recent N items will be returned.

    ::

        {# Fetch 10 most recent items #}
        {% get_timeline_items limit 10 as items %}

    Newer items will be first in the list (i.e. ordered by timstamp descending)
    unless you ask for them to be reversed::

        {# Fetch the 10 earliest items #}
        {% get_timeline_items limit 10 reversed as items %}

    You can also fetch items between two given dates::

        {% get_timeline_items between "2007-01-01" and "2007-01-31" as items %}

    Dates can be in any format understood by ``dateutil.parser``, and can of
    course be variables. UserTimelineItems must be limited in some way; you must either pass
    ``limit`` or ``between``.

    Dates can also be the magic strings "now" or "today"::

        {% get_timeline_items between "2007-01-01" and "today" as items %}

    You can also limit items by type::

        {# Fetch the 10 most recent videos and photos #}
        {% get_timelins_items oftype video oftype photo limit 10 as items %}

    ``oftype`` can be given as many times as you like; only those types will be
    returned. The arguments to ``oftype`` are the lowercased class names of
    timelines'd items. 

    You can similarly exclude types using ``excludetype``::

        {# Fetch the 10 most items that are not videos #}
        {% get_timeline_items excludetype video limit 10 as items %}

    You can give ``excludetype`` as many times as you like, but it is an error
    to use both ``oftype`` and ``excludetype`` in the same tag invocation.
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
                    model_list.append(UserTimelineItem.objects.models_by_name[name])
                except KeyError:
                    raise template.TemplateSyntaxError("%r tag: invalid model name: %r" % (tagname, name))
            args[arg] = model_list

    return GetAggregatorUserTimelineItemsNode(**args)

class GetAggregatorUserTimelineItemsNode(template.Node):
    def __init__(self, asvar, foruser=None, limit=None, start=None, end=None, oftypes=[], excludetypes=[], reversed=False):
        self.asvar = asvar
        self.foruser = foruser
        self.limit = limit
        self.start = start
        self.end = end
        self.oftypes = oftypes
        self.excludetypes = excludetypes
        self.reversed = reversed

    def render(self, context):
        qs = UserTimelineItem.objects.all()

        # Handle user if given
        if self.foruser:
          user = resolve_variable(self.foruser, context)
          qs = qs.filter(user=user)

        # Handle start/end dates if given
        if self.start:
            start = self.resolve_date(self.start, context)
            end = self.resolve_date(self.end, context)
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
