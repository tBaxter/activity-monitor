"""
Based loosely on Jacob Kaplan-Moss' old Jellyroll application, probably by way of Jeff Croft. 
The origins are hazy at this point.

"""
import calendar
import datetime

from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.views.generic import ListView

from .models import Activity

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
        qs = super(ActionList, self).get_queryset(*args, **kwargs).order_by('-timestamp').select_related('user')
        if 'user' in kwargs:
            qs = qs.filter(actor_name=kwargs['user'])
        return qs
action_list = ActionList.as_view()


class ActionsForPeriod(ActionList):
    previous = None
    template_name = "activity_monitor/grouped.html"

    def dispatch(self, request, *args, **kwargs):
        self.day   = int(kwargs['day']) if 'day' in kwargs else None
        self.month = int(kwargs['month']) if 'month' in kwargs else datetime.date.today().month
        self.year  = int(kwargs['year']) if 'year' in kwargs else datetime.date.today().year
        self.page  = kwargs.get('page', 1)
        return super(ActionsForPeriod, self).dispatch(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super(ActionsForPeriod, self).get_queryset(*args, **kwargs).order_by('-timestamp').select_related('user')

        if self.day: # Get actions for a particular day
            qs = qs.filter(timestamp__year=self.year, timestamp__month=self.month, timestamp__day=self.day)
            self.previous = datetime.date(self.year, self.month, self.day) - datetime.timedelta(days=1)
        else:
            # Get actions for a particular month
            start_date = datetime.date(self.year, self.month, 1)
            end_date   = datetime.date(self.year, self.month, calendar.monthrange(self.year, self.month)[1])
            qs = qs.filter(timestamp__gte=start_date, timestamp__lte=end_date)
        return qs


    def get_context_data(self, **kwargs):
        context = super(ActionsForPeriod, self).get_context_data(**kwargs)
        context['previous'] = self.previous

        # the QS is used for pagination, so let's reorganize and group them here
        qs = self.get_queryset()
        actions = OrderedDict()
        for item in qs:
            if item.target not in actions.keys():
                actions[item.target] = {
                    'item': item,
                    'actors': [item.actor_name],
                    'actor_count': 0,
                    'verb': item.override_string if item.override_string else item.verb,
                    'last_modified': item.timestamp
                }
            else: # item added, but update attributes
                if item.actor_name not in actions[item.target]['actors']:
                    actions[item.target]['actors'].append(item.actor_name)
                    actions[item.target]['actor_count'] += 1
                if actions[item.target]['last_modified'] < item.timestamp:
                    actions[item.target]['last_modified'] = item.timestamp
    
        context['actions'] = actions
        return context
actions_for_period = ActionsForPeriod.as_view()



class ActionsForToday(ActionsForPeriod):
    def get_queryset(self, *args, **kwargs):
        today = datetime.date.today();
        qs = super(ActionsForToday, self).get_queryset(*args, **kwargs).filter(timestamp__year=today.year, timestamp__month=today.month, timestamp__day=today.day)
        return qs
actions_for_today = ActionsForToday.as_view()

