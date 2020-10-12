from django.urls import include, path
from rest_framework_nested import routers

from api.views import *

router = routers.DefaultRouter()
router.register(r'questions', QuestionViewSet, basename="question")

question_router = routers.NestedDefaultRouter(router, r'questions', lookup='questions')
question_router.register(r'answers', AnswerViewSet, basename='question-answers')

app_name = 'api'

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('', include(question_router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
