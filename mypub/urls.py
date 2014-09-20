from django.conf.urls import patterns, url

from mypub import views

urlpatterns = patterns('', url(r'^$', views.index, name='mypub'),
	url(r'^(?P<aid>\d+)/$', views.detail),
	url(r'^search$', views.search),
#	url(r'^meta$', views.display_meta),
#	url(r'^search-form$', views.search_form),
)
