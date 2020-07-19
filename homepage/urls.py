from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ask$', views.ask_view, name='ask'),
    url(r'^question_(?P<question_id>[0-9]+)/$', views.question_view, name='question_detail'),
    url(r'^signup$', views.signup_view, name='signup'),
    url(r'^settings$', views.settings_view, name='settings'),
]