from django.conf.urls import patterns, include, url
from django.contrib import admin
from mysite import views

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', views.index, name='root page'),
	url(r'^contact/', views.contact),
	url(r'^publication/', include('mypub.urls')),
	url(r'^admin/', include(admin.site.urls)),
)


#from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#urlpatterns += staticfiles_urlpatterns()

from django.conf import settings

if settings.DEBUG:
	urlpatterns += patterns('django.contrib.staticfiles.views',
		url(r'^static/(?P<path>.*)$', 'serve'),)
