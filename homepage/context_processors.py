from django.db.models import Sum
from django.db.models.functions import Coalesce

from .models import Question
from Hasker.settings import MEDIA_URL, STATIC_IMAGES_URL


def trending_questions(request):
    trending_question_list = Question.objects.annotate(vote_sum=Coalesce(Sum('questionvote__value'), 0)). \
            filter(vote_sum__gt=0). \
            order_by('-vote_sum', 'create_date').values('id', 'header', 'vote_sum')[:20]
    return {'trending_question_list': trending_question_list, 'media_url': MEDIA_URL,
            'static_img_url': STATIC_IMAGES_URL}
