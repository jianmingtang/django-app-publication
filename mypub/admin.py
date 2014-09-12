from django.contrib import admin

# Register your models here.

from mypub.models import *

class PubAdmin(admin.ModelAdmin):
	list_display = ('Category', 'Title', 'Author','Journal', 'Volume', 'Page','Year','Link')
	fieldsets = [
		('Category', {'fields': ['Category']}),
		('Title',    {'fields': ['Title']}),
		('Author',   {'fields': ['Author']}),
		('Journal',  {'fields': ['Journal']}),
		('Volume',   {'fields': ['Volume']}),
		('Page',     {'fields': ['Page']}),
		('Year',     {'fields': ['Year']}),
		('Link',     {'fields': ['Link']}),
	]
	list_filter = ['Year']
	search_fields = ['Title','Arthur','Journal']

admin.site.register(Publication, PubAdmin)

