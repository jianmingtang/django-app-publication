from django.conf.urls import patterns, url

from mypub import views

urlpatterns = patterns('', url(r'^$', views.index, name='index'),
	url(r'^(?P<mypub_id>\d+)/$', views.detail, name='detail'),
)
