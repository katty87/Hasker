from django.urls import include, path
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenObtainPairView

from api.views import *

router = routers.DefaultRouter()
router.register(r'questions', QuestionViewSet, basename="question")
router.register(r'questions/trending', TrendingQuestionViewSet, basename="question-trending")
router.register(r'questions/hot', HotQuestionViewSet, basename="question-hot")
router.register(r'questions/new', NewQuestionViewSet, basename="question-new")

question_router = routers.NestedDefaultRouter(router, r'questions', lookup='questions')
question_router.register(r'answers', AnswerViewSet, basename='question-answers')

app_name = 'api'

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('questions/trending/', TrendingQuestionViewSet.as_view({'get': 'list'})),
    path('questions/hot/', HotQuestionViewSet.as_view({'get': 'list'})),
    path('questions/new/', NewQuestionViewSet.as_view({'get': 'list'})),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]

urlpatterns += router.urls
urlpatterns += question_router.urls
