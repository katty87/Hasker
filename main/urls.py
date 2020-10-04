from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^ask$', views.AskQuestionView.as_view(), name='ask'),
    url(r'^question/(?P<pk>[0-9]+)/$', views.QuestionDetailView.as_view(), name='question_detail'),
    url(r'^question/(?P<pk>[0-9]+)/answer/$', views.answer_question, name='answer_question'),
    url(r'^search$', views.SearchResultsView.as_view(), name='search_results'),
    url(r'^ajax/vote/question/$', views.vote_question, name='vote_question'),
    url(r'^ajax/vote/answer/$', views.vote_answer, name='vote_answer'),
    url(r'^ajax/answer/set-correct/$', views.mark_answer_right, name='mark_answer_right'),
]
