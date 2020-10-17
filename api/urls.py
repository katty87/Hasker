from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from api.views import *

app_name = 'api'

schema_view = get_schema_view(
   openapi.Info(
      title="Hasker API",
      default_version='v1',
      terms_of_service="https://www.google.com/policies/terms/",
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

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
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

