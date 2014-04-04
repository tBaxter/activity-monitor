import datetime
from datetime import date, timedelta

from django import template

register = template.Library()


from datetime import date, timedelta

def get_last_day_of_month(year, month):
    if (month == 12):
        year += 1
        month = 1
    else:
        month += 1
    return date(year, month, 1) - timedelta(1)


@register.inclusion_tag('activity_monitor/inclusion/calendar.html', takes_context=True)
def calendar(context, year=date.today().year, month=date.today().month, active_day=date.today().day):
    """ Inclusion tag which renders the template activity_monitor/inclusion/calendar.html to build a calendar. """
    today = date.today()
    active_day = active_day
    first_day_of_month = date(year, month, 1)
    last_day_of_month = get_last_day_of_month(year, month)
    first_day_of_calendar = first_day_of_month - timedelta(first_day_of_month.weekday()+1)
    last_day_of_calendar = last_day_of_month + timedelta(7 - last_day_of_month.weekday())

    month_cal = []
    week = []
    week_headers = []

    i = 0
    day = first_day_of_calendar
    while day <= last_day_of_calendar:
        if i < 7:
            week_headers.append(day)
        cal_day = {}
        cal_day['day'] = day
        if day.month == month:
            cal_day['in_month'] = True
        else:
            cal_day['in_month'] = False
        if day == today:
              cal_day['is_today'] = True
        else:
            cal_day['is_today'] = False
        if day > today:
              cal_day['in_future'] = True
        else:
            cal_day['in_future'] = False
        if active_day:
          if day == active_day:
                cal_day['is_active'] = True
          else:
              cal_day['is_active'] = False
        week.append(cal_day)
        if day.weekday() == 5:
            month_cal.append(week)
            week = []
        i += 1
        day += timedelta(1)

    return {
      'month': first_day_of_month,
      'previous_month': (first_day_of_month - datetime.timedelta(days=1)).replace(day=1),
      'next_month': last_day_of_month + datetime.timedelta(days=1),
      'calendar': month_cal, 
      'calendar_headers': week_headers,
      'timeline_for': context['timeline_for'],
    }