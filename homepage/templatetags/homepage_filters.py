from django import template
from django.contrib.auth.models import User
from homepage.models import Answer

register = template.Library()


@register.filter(name='get_current_user_vote')
def get_current_user_vote(object, user_id):
    if type(object) is Answer:
        return object.current_user_vote(user_id)

    return None
