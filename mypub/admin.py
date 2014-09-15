from django.contrib import admin

from mypub.models import *

class PubAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'abstract')
	fieldsets = [
		('Title',    {'fields': ['title']}),
		('Author',   {'fields': ['author']}),
		('Abstract', {'fields': ['abstract']}),
	]
#	list_filter = ['Year']
	search_fields = ['title','author','abstract']

admin.site.register(Article, PubAdmin)

