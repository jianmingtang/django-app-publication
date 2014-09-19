from django.conf.urls import patterns, url

from mypub import views

urlpatterns = patterns('', url(r'^$', views.index, name='index'),
	url(r'^(?P<aid>\d+)/$', views.detail, name='detail'),
#	url(r'^meta$', views.display_meta),
#	url(r'^search-form$', views.search_form),
#	url(r'^search$', views.search),
)
