"""
Based loosely on Jacob Kaplan-Moss' old Jellyroll application, probably by way of Jeff Croft.
The origins are hazy at this point.

"""
import calendar
import datetime

from django.contrib.auth import get_user_model
from django.views.generic import ListView

from .models import Activity
from .utils import group_activities

UserModel = get_user_model()


class ActionList(ListView):
    """
    Provides a basic list view for a list of tracked actions
    Subclassed a lot below.
    """
    queryset = Activity.objects.all()
    template_name = "activity_monitor/activity_list.html"
    paginate_by = 100
    allow_empty = True

    def get_queryset(self, *args, **kwargs):
        qs = super(ActionList, self).get_queryset(*args, **kwargs).order_by('-timestamp').select_related('actor')
        if 'user' in kwargs:
            qs = qs.filter(actor_name=kwargs['user'])
        return qs
action_list = ActionList.as_view()


class ActionsForPeriod(ActionList):
    previous = None
    template_name = "activity_monitor/grouped.html"
    next = None
    previous = None

    def dispatch(self, request, *args, **kwargs):
        self.day   = int(kwargs['day']) if 'day' in kwargs else None
        self.month = int(kwargs['month']) if 'month' in kwargs else datetime.date.today().month
        self.year  = int(kwargs['year']) if 'year' in kwargs else datetime.date.today().year
        self.page  = kwargs.get('page', 1)
        self.current_day = datetime.date.today()
        return super(ActionsForPeriod, self).dispatch(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super(ActionsForPeriod, self).get_queryset(*args, **kwargs).order_by('-timestamp').select_related('actor')

        if self.day: # Get actions for a particular day
            qs = qs.filter(timestamp__year=self.year, timestamp__month=self.month, timestamp__day=self.day)
            self.current_day = datetime.date(self.year, self.month, self.day)
            self.previous = self.current_day - datetime.timedelta(days=1)
            if self.current_day == datetime.date.today():
                self.next = None
            else:
                self.next = self.current_day + datetime.timedelta(days=1)
        else:
            # Get actions for a particular month
            start_date = datetime.date(self.year, self.month, 1)
            end_date   = datetime.date(self.year, self.month, calendar.monthrange(self.year, self.month)[1])
            qs = qs.filter(timestamp__gte=start_date, timestamp__lte=end_date)
        return qs


    def get_context_data(self, **kwargs):
        context = super(ActionsForPeriod, self).get_context_data(**kwargs)
        context['previous_day'] = self.previous
        context['next_day'] = self.next

        # the QS is used for pagination, so let's reorganize and group them here
        context['actions'] = group_activities(self.get_queryset())
        if self.day:
            context['current_date_string'] = self.current_day.strftime('%B %d %Y')
        else:
            context['current_date_string'] = datetime.date(self.year, self.month, 1).strftime('%B %Y')
        return context
actions_for_period = ActionsForPeriod.as_view()



class ActionsForToday(ActionsForPeriod):
    def get_queryset(self, *args, **kwargs):
        today = datetime.datetime.now() - datetime.timedelta(hours = 24)
        qs = super(ActionsForToday, self).get_queryset(*args, **kwargs)
        qs = qs.filter(timestamp__gte=today)
        return qs

    def get_context_data(self, **kwargs):
        context = super(ActionsForToday, self).get_context_data(**kwargs)

        # the QS is used for pagination, so let's reorganize and group them here
        context['actions'] = group_activities(self.get_queryset())
        return context
actions_for_today = ActionsForToday.as_view()

