from django.db import models
from django.contrib import admin
from django.forms import forms, Textarea
from mypub.models import Article, Journal, VJ, URL

class LargeTextarea(forms.Textarea):
	def __init__(self, *args, **kwargs):
		attrs = kwargs.setdefault('attrs', {})
		attrs.setdefault('rows', 20)
		attrs.setdefault('cols', 100)
		super(LargeTextarea, self).__init__(*args, **kwargs)

class ArticleAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'abstract', 'journal')
	fieldsets = [
		('Article',  {'fields': ['title', 'author']}),
		('abstract', {'fields': ['abstract']}),
	]
	search_fields = ['title','author','abstract']
	formfield_overrides = {
		models.TextField: {'widget': LargeTextarea},
	}

class JournalAdmin(admin.ModelAdmin):
	list_display = ('title', 'volume', 'page', 'year', 'link')
	list_filter = ['year']
	search_fields = ['title']

class VJAdmin(admin.ModelAdmin):
	list_display = ('article', 'title', 'volume', 'issue', 'year')
	list_filter = ['title', 'year']
	search_fields = ['title']

class URLAdmin(admin.ModelAdmin):
	list_display = ('article', 'name', 'link')
#	formfield_overrides = {
#		models.CharField: {'widget': TextInput(attrs={'cols':'20'})},
#	}

admin.site.register(Article, ArticleAdmin)
admin.site.register(Journal, JournalAdmin)
admin.site.register(VJ, VJAdmin)
admin.site.register(URL, URLAdmin)

