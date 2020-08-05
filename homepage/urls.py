from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^ask$', views.ask_view, name='ask'),
    url(r'^question/(?P<pk>[0-9]+)/$', views.QuestionDetailView.as_view(), name='question_detail'),
    url(r'^question/(?P<pk>[0-9]+)/answer/$', views.answer_question, name='answer_question'),
    url(r'^signup$', views.signup_view, name='signup'),
    url(r'^settings/(?P<pk>[0-9]+)/$', views.SettingsView.as_view(), name='settings'),
    url(r'^search$', views.SearchResultsView.as_view(), name='search_results'),
    url(r'^ajax/vote/question/$', views.vote_question, name='vote_question'),
    url(r'^ajax/vote/answer/$', views.vote_answer, name='vote_answer'),
]