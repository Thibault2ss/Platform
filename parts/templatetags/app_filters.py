from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter(name='get_due_date_string')
def get_due_date_string(value):
    delta = value.date() - date.today()

    if delta.days == 0:
        return "Today!"
    elif delta.days < 1:
        return "%s %s ago!" % (abs(delta.days),
            ("day" if abs(delta.days) == 1 else "days"))
    elif delta.days == 1:
        return "Tomorrow"
    elif delta.days > 1:
        return "In %s days" % delta.days

@register.filter(name='seconds_to_duration')
def seconds_to_duration(value):
    hours = value//3600
    minutes = (value % 3600)//60
    print "MINUTE: %s"%minutes

    return "%s h %s m"%(hours, minutes)
