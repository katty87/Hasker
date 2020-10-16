from django.urls import include, path
from django.conf.urls import url
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenObtainPairView

from api.views import *

app_name = 'api'

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^questions/$', QuestionViewSet.as_view(), name="questions"),
    url(r'^questions/(?P<id>[0-9]+)/$', QuestionDetailView.as_view(), name="question-detail"),
    url(r'^questions/(?P<id>\d*?)/answers/$', AnswerViewSet.as_view(), name="question-answers"),
    url(r'^questions/trending/$', TrendingQuestionViewSet.as_view(), name="questions-trending"),
    url(r'^questions/hot/$', HotQuestionViewSet.as_view(), name="questions-hot"),
    url(r'^questions/new/$', NewQuestionViewSet.as_view(), name="questions-new"),
    url(r'^token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]

