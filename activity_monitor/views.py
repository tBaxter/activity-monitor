"""
Views for looking at Activity items by date.

Based on Jacob Kaplan-Moss' Jellyroll application.

These act as kinda-sorta generic views in that they take a number of the same
arguments as generic views do (i.e. ``template_name``, ``extra_context``, etc.)

They all also take an argument ``queryset`` which should be an ``Activity``
queryset; it'll be used as the *starting point* for the the view in question
instead of ``Activity.objects.all()``.
"""

import time
import datetime

from django.core import urlresolvers
from django.template import loader, RequestContext
from django.http import Http404, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Activity


def get_feed_url_for_view(model_string):
    feed_base_url = urlresolvers.reverse('timelines_feeds', args=('latest-items',))
    if model_string == "default":
        feed_url = feed_base_url
    else:
        feed_url = feed_base_url + "?models=" + model_string
    return feed_url


def get_timelines_content_types(type_set="default"):
    content_types = []
    for item in settings.ACTIVITY_MONITOR_MODELS:
        app_label     = item['model'].split('.')[0]
        model         = item['model'].split('.')[1]
        content_type  = ContentType.objects.get(app_label=app_label, model=model)
        content_types.append(content_type)
    return content_types


def filter_queryset_by_model_list(queryset, model_list):
    model_list = model_list
    if type(model_list) != type([]):
        model_list = model_list.split(",")
    requested_content_types = []
    content_types = []
    for item in model_list:
        try:
            app_label     = item.split('.')[0]
            model         = item.split('.')[1]
            content_type  = ContentType.objects.get(app_label=app_label, model=model)
            requested_content_types.append(content_type)
        except:
            pass
        for content_type in get_timelines_content_types(type_set="all"):
            if content_type in requested_content_types:
                content_types.append(content_type)
        return (queryset.filter(content_type__in=content_types), content_types)


def filter_view_by_models(queryset, model_query, model_query_list):
  if model_query == "default":
    content_types = get_timelines_content_types(type_set="default")
    model_list = [ ct.app_label + "." + ct.model for ct in content_types]
    queryset, content_types = filter_queryset_by_model_list(queryset, model_list)
    model_string = "default"
  elif model_query == "all":
    model_string = "all"
    content_types = get_timelimes_content_types(type_set="all")
  else:
    model_string = ",".join(model_query_list)
    model_list = model_query_list
    queryset, content_types = filter_queryset_by_model_list(queryset, model_list)
  return (queryset, content_types, model_string)


def today(request, **kwargs):
    """
    Activitys from today
    
    See :view:`timelines.views.day`
    """
    y, m, d = datetime.date.today().strftime("%Y/%b/%d").lower().split("/")
    if "template_name" not in kwargs:
        kwargs['template_name'] = "activity_monitor/today.html"
    return day(request, y, m, d, recent_first=True, **kwargs)


def archive(request, queryset=None,
    template_name="activity_monitor/archive.html", template_loader=loader,
    extra_context=None, context_processors=None, mimetype=None, username=None):
    """
    Activitys for forever.

    Works a bit like a generic view in that you can pass a bunch of optional
    keyword arguments which work just like they do in generic views. Those
    arguments are: ``template_name``, ``template_loader``, ``extra_context``,
    ``context_processors``, and ``mimetype``.

    You can also pass a ``queryset`` argument; see the module's docstring
    for information about how that works.

    Templates: ``activity_monitor/archive.html`` (default)
    Context:
        ``items``
            Items, earliest first.
        ``date_list``
            List of years that have Activitys.
        ``all_content_types``
            List of all ContentTypes objects available to the timelines
        ``content_types``
            List of ContentTypes objects used to render this page
        ``model_string``
            String representation of models appearing on this page (useful as a cache key argument)
            
    """
    # Handle the initial queryset
    if not queryset:
        queryset = Activity.objects.all()
    if queryset.order_by is None:
        queryset = queryset.order_by("-timestamp")
        
    if username:
      user = get_object_or_404(User, username=username)
      queryset = queryset.filter(user=user)
    else:
      user = None

    date_list = queryset.dates('timestamp', 'year')[::-1]
    
    # Filtering by model
    model_query = request.GET.get('models', 'default')
    model_query_list = request.GET.getlist('models')
    queryset, content_types, model_string = filter_view_by_models(queryset, model_query, model_query_list)
    
    # Build the feed URL for this view
    try:
      feed_url = get_feed_url_for_view(model_string)
    except:
      feed_url= ''
    
    # Build the context
    context = RequestContext(request, {
        "items" : queryset.order_by("-timestamp"),
        "date_list" : date_list,
        "all_content_types"  : get_timelines_content_types(type_set='all'),
        "content_types" : content_types,
        "model_string" : model_string,
        "feed_url": feed_url,
        "timeline_for": user,
    }, context_processors)
    if extra_context:
        for key, value in extra_context.items():
            if callable(value):
                context[key] = value()
            else:
                context[key] = value

    # Load, render, and return
    t = template_loader.get_template(template_name)
    return HttpResponse(t.render(context), mimetype=mimetype)



def year(request, year, queryset=None,
    template_name="activity_monitor/year.html", template_loader=loader,
    extra_context=None, context_processors=None, mimetype=None, username=None):
    """
    Activitys for a particular year.

    Works a bit like a generic view in that you can pass a bunch of optional
    keyword arguments which work just like they do in generic views. Those
    arguments are: ``template_name``, ``template_loader``, ``extra_context``,
    ``context_processors``, and ``mimetype``.
    
    You can also pass a ``queryset`` argument; see the module's docstring
    for information about how that works.

    Templates: ``activity_monitor/year.html`` (default)
    Context:
        ``items``
            Items from the year, earliest first.
        ``year``
            The year.
        ``previous``
            The previous year; ``None`` if that year was before jellyrolling
            started..
        ``previous_link``
            Link to the previous year
        ``next``
            The next year; ``None`` if it's in the future.
        ``next_year``
            Link to the next year
        ``date_list``
            List of months in the current year.
        ``all_content_types``
            List of all ContentTypes objects available to the timelines
        ``content_types``
            List of ContentTypes objects used to render this page
        ``model_string``
            String representation of models appearing on this page (useful as a cache key argument)
    """
    # Make sure we've requested a valid year
    year = int(year)
    try:
        first = Activity.objects.order_by("timestamp")[0]
    except IndexError:
        raise Http404("No items; no views.")
    today = datetime.date.today()
    if year < first.timestamp.year or year > today.year:
        raise Http404("Invalid year (%s .. %s)" % (first.timestamp.year, today.year))
    
    # Calculate the previous year
    previous = year - 1
    if username:
      previous_link = urlresolvers.reverse("timelines_year_user", kwargs={'year': previous, 'username': username })
    else:
      previous_link = urlresolvers.reverse("timelines_year", args=[previous])
    if previous < first.timestamp.year:
        previous = previous_link = None
    
    # And the next year
    next = year + 1
    if username:
      next_link = urlresolvers.reverse("timelines_year_user", kwargs={'year': next, 'username': username })
    else:
      next_link = urlresolvers.reverse("timelines_year", args=[next])
    if next > today.year:
        next = next_link = None
        
    # Handle the initial queryset
    if not queryset:
        queryset = Activity.objects.all()
    queryset = queryset.filter(timestamp__year=year)
    if queryset.order_by is None:
        queryset = queryset.order_by("timestamp")
    
    if username:
      user = get_object_or_404(User, username=username)
      queryset = queryset.filter(user=user)
    else:
      user = None
      
    date_list = queryset.dates('timestamp', 'month')
    
    # Filtering by model
    model_query = request.GET.get('models', 'default')
    model_query_list = request.GET.getlist('models')
    queryset, content_types, model_string = filter_view_by_models(queryset, model_query, model_query_list)
    
    # Build the feed URL for this view
    try:
      feed_url = get_feed_url_for_view(model_string)
    except:
      feed_url= ''
    
    # Build the context
    context = RequestContext(request, {
        "items"         : queryset.filter(timestamp__year=year).order_by("timestamp"),
        "year"          : year,
        "previous_year"      : previous,
        "previous_year_link" : previous_link,
        "next_year"          : next,
        "next_year_link"     : next_link,
        "date_list"          : date_list,
        "all_content_types"  : get_timelines_content_types(type_set="all"),
        "content_types" : content_types,
        "model_string" : model_string,
        "feed_url": feed_url,
        "timeline_for": user,
    }, context_processors)
    if extra_context:
        for key, value in extra_context.items():
            if callable(value):
                context[key] = value()
            else:
                context[key] = value
    
    # Load, render, and return
    t = template_loader.get_template(template_name)
    return HttpResponse(t.render(context), mimetype=mimetype)

def month(request, year, month, queryset=None,
    template_name="activity_monitor/month.html", template_loader=loader,
    extra_context=None, context_processors=None, mimetype=None, username=None):
    """
    Activitys for a particular month.

    Works a bit like a generic view in that you can pass a bunch of optional
    keyword arguments which work just like they do in generic views. Those
    arguments are: ``template_name``, ``template_loader``, ``extra_context``,
    ``context_processors``, and ``mimetype``.
    
    You can also pass a ``queryset`` argument; see the module's docstring
    for information about how that works.

    Templates: ``activity_monitor/month.html`` (default)
    Context:
        ``items``
            Items from the month, earliest first.
        ``month``
            The month (a ``datetime.date`` object).
        ``previous``
            The previous month; ``None`` if that month was before jellyrolling
            started.
        ``previous_link``
            Link to the previous month
        ``next``
            The next month; ``None`` if it's in the future.
        ``next_link``
            Link to the next month
        ``all_content_types``
            List of all ContentTypes objects available to the timelines
        ``content_types``
            List of ContentTypes objects used to render this page
        ``model_string``
            String representation of models appearing on this page (useful as a cache key argument)
    """
    # Make sure we've requested a valid month
    try:
        date = datetime.date(*time.strptime(year+month, '%Y%b')[:3])
    except ValueError:
        raise Http404("Invalid month string")
    try:
        first = Activity.objects.order_by("timestamp")[0]
    except IndexError:
        raise Http404("No items; no views.")
    
    # Calculate first and last day of month, for use in a date-range lookup.
    today = datetime.date.today()
    first_day = date.replace(day=1)
    if first_day.month == 12:
        last_day = first_day.replace(year=first_day.year + 1, month=1)
    else:
        last_day = first_day.replace(month=first_day.month + 1)
    
    if first_day < first.timestamp.date().replace(day=1) or date > today:
        raise Http404("Invalid month (%s .. %s)" % (first.timestamp.date(), today))

    # Calculate the previous month
    previous = (first_day - datetime.timedelta(days=1)).replace(day=1)
    if username:
      previous_link = urlresolvers.reverse("timelines_month_user", kwargs={ 'year': previous.strftime("%Y"), 'month': previous.strftime("%b").lower(), 'username': username })
    else:
      previous_link = urlresolvers.reverse("timelines_month", args=previous.strftime("%Y %b").lower().split())
    if previous < first.timestamp.date().replace(day=1):
        previous = None
    
    # And the next month
    next = last_day + datetime.timedelta(days=1)
    if username:
      next_link = urlresolvers.reverse("timelines_month_user", kwargs={ 'year': next.strftime("%Y"), 'month': next.strftime("%b").lower(), 'username': username })
    else:
      next_link = urlresolvers.reverse("timelines_month", args=next.strftime("%Y %b").lower().split())
    if next > today:
        next = None
        
    # Handle the initial queryset
    if not queryset:
        queryset = Activity.objects.all()
    queryset = queryset.filter(timestamp__range=(first_day, last_day))
    if queryset.order_by is None:
        queryset = queryset.order_by("timestamp")
    
    if username:
      user = get_object_or_404(User, username=username)
      queryset = queryset.filter(user=user)
    else:
      user = None
      
    # Filtering by model
    model_query = request.GET.get('models', 'default')
    model_query_list = request.GET.getlist('models')
    queryset, content_types, model_string = filter_view_by_models(queryset, model_query, model_query_list)

    # Build the feed URL for this view
    try:
      feed_url = get_feed_url_for_view(model_string)
    except:
      feed_url= ''
    
    # Build the context
    context = RequestContext(request, {
        "items"         : queryset,
        "month"         : date,
        "previous_month"      : previous,
        "previous_month_link" : previous_link,
        "next_month"          : next,
        "next_month_link"     : next_link,
        "all_content_types"  : get_timelines_content_types(type_set="all"),
        "content_types" : content_types,
        "model_string" : model_string,
        "feed_url": feed_url,
        "timeline_for": user,
    }, context_processors)
    if extra_context:
        for key, value in extra_context.items():
            if callable(value):
                context[key] = value()
            else:
                context[key] = value
    
    # Load, render, and return
    t = template_loader.get_template(template_name)
    return HttpResponse(t.render(context), mimetype=mimetype)
        
def day(request, year, month, day, queryset=None, recent_first=True,
    template_name="activity_monitor/day.html", template_loader=loader,
    extra_context=None, context_processors=None, mimetype=None, username=None):
    """
    Activitys for a particular day.

    Works a bit like a generic view in that you can pass a bunch of optional
    keyword arguments which work just like they do in generic views. Those
    arguments are: ``template_name``, ``template_loader``, ``extra_context``,
    ``context_processors``, and ``mimetype``.
    
    Also takes a ``recent_first`` param; if it's ``True`` the newest items
    will be displayed first; otherwise items will be ordered earliest first.

    You can also pass a ``queryset`` argument; see the module's docstring
    for information about how that works.

    Templates: ``activity_monitor/day.html`` (default)
    Context:
        ``items``
            Items from the month, ordered according to ``recent_first``.
        ``day``
            The day (a ``datetime.date`` object).
        ``previous``
            The previous day; ``None`` if that day was before aggregating
            started.
        ``previous_link``
            Link to the previous day
        ``next``
            The next day; ``None`` if it's in the future.
        ``next_link``
            Link to the next day.
        ``is_today``
            ``True`` if this day is today.            
        ``all_content_types``
            List of all ContentTypes objects available to the timelines
        ``content_types``
            List of ContentTypes objects used to render this page
        ``model_string``
            String representation of models appearing on this page (useful as a cache key argument)
    """
    # Make sure we've requested a valid month
    try:
        day = datetime.date(*time.strptime(year+month+day, '%Y%b%d')[:3])
    except ValueError:
        raise Http404("Invalid day string")
    try:
        first = Activity.objects.order_by("timestamp")[0]
    except IndexError:
        raise Http404("No items; no views.")
    
    today = datetime.date.today()
    if day < first.timestamp.date() or day > today:
        raise Http404("Invalid day (%s .. %s)" % (first.timestamp.date(), today))
    
    # Calculate the previous day
    previous = day - datetime.timedelta(days=1)
    if username:
      previous_link = urlresolvers.reverse("timelines_day_user", kwargs={'year':previous.strftime("%Y"), 'month': previous.strftime("%b").lower(), 'day': previous.strftime("%d")})
    else:
      previous_link = urlresolvers.reverse("timelines_day", args=previous.strftime("%Y %b %d").lower().split())
    if previous < first.timestamp.date():
        previous = previous_link = None
    
    # And the next month
    next = day + datetime.timedelta(days=1)
    if username:
      next_link = urlresolvers.reverse("timelines_day_user", kwargs={'year':next.strftime("%Y"), 'month': next.strftime("%b").lower(), 'day': next.strftime("%d")})
    else:
      next_link = urlresolvers.reverse("timelines_day", args=next.strftime("%Y %b %d").lower().split())
    if next > today:
        next = next_link = None
    
    # Some lookup values...
    timestamp_range = (datetime.datetime.combine(day, datetime.time.min), 
                       datetime.datetime.combine(day, datetime.time.max))
    
    # Handle the initial queryset
    if not queryset:
       queryset = Activity.objects.all()
    queryset = queryset.filter(timestamp__range=timestamp_range)
    if queryset.order_by is None:
        if recent_first:
            queryset = queryset.order_by("-timestamp")
        else:
            queryset = queryset.order_by("timestamp")
    
    if username:
      user = get_object_or_404(User, username=username)
      queryset = queryset.filter(user=user)
    else:
      user = None
      
    # Filtering by model
    model_query = request.GET.get('models', 'default')
    model_query_list = request.GET.getlist('models')
    queryset, content_types, model_string = filter_view_by_models(queryset, model_query, model_query_list)

    # Build the feed URL for this view
    try:
      feed_url = get_feed_url_for_view(model_string)
    except:
      feed_url= ''
    
    # Build the context
    context = RequestContext(request, {
        "items"         : queryset,
        "day"           : day,
        "previous_day"      : previous,
        "previous_day_link" : previous_link,
        "next_day"          : next,
        "next_day_link"     : next_link,
        "is_today"      : day == today,
        "all_content_types"  : get_timelines_content_types(type_set="all"),
        "content_types" : content_types,
        "model_string" : model_string,
        "feed_url": feed_url,
        "timeline_for": user,
    }, context_processors)
    if extra_context:
        for key, value in extra_context.items():
            if callable(value):
                context[key] = value()
            else:
                context[key] = value
    
    # Load, render, and return
    t = template_loader.get_template(template_name)
    return HttpResponse(t.render(context), mimetype=mimetype)