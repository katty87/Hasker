from datetime import datetime

from django import template
from django.db.models import Sum

from main.models import QuestionVote

register = template.Library()


@register.filter(name='get_question_vote_sum')
def get_question_vote_sum(object, question_id):
    return QuestionVote.objects.filter(question_id=question_id).aggregate(Sum('value'))


@register.filter(name='split')
def split(value, key):
    if value:
        return value.split(key)
    else:
        return None


@register.filter(name='get_answered_date_string')
def get_answered_date_string(value):
    delta = datetime.utcnow() - value

    if delta.days == 0:
        if delta.seconds < 60:
            return '{} {} ago'.format(delta.seconds, ("second" if delta.seconds == 1 else "seconds"))

        minutes = delta.seconds // 60
        if minutes < 60:
            return '{} {} ago'.format(minutes, ("minute" if minutes == 1 else "minutes"))

        hours = delta.seconds // 3600
        return '{} {} ago'.format(hours, ("hour" if hours == 1 else "hours"))
    elif delta.days < 0:
        return "in future"
    elif 1 <= delta.days < 7:
        return "{} {} ago".format(abs(delta.days), ("day" if abs(delta.days) == 1 else "days"))
    elif delta.days < 29:
        weeks = delta.days // 7
        return "{} {} ago".format(weeks, ("week" if weeks == 1 else "weeks"))
    else:
        return value.strftime("%b %d'%y")

