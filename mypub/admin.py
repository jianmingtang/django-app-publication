from django.contrib import admin

from mypub.models import Article, Journal, VJ, URL

class ArticleAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'abstract', 'journal')
	fieldsets = [
		('title',    {'fields': ['title']}),
		('author',   {'fields': ['author']}),
		('abstract', {'fields': ['abstract']}),
	]
#	list_filter = ['year']
	search_fields = ['title','author','abstract']

class JournalAdmin(admin.ModelAdmin):
	list_display = ('title', 'volume', 'page', 'year', 'link')
#	fieldsets = [
#		('title',    {'fields': ['title']}),
#		('volume',   {'fields': ['volume']}),
#		('page', {'fields': ['page']}),
#		('year', {'fields': ['year']}),
#	]
	list_filter = ['year']
	search_fields = ['title']

class VJAdmin(admin.ModelAdmin):
	list_display = ('article', 'title', 'volume', 'issue', 'year')
	list_filter = ['title', 'year']
	search_fields = ['title']

class URLAdmin(admin.ModelAdmin):
	list_display = ('article', 'name', 'link')

admin.site.register(Article, ArticleAdmin)
admin.site.register(Journal, JournalAdmin)
admin.site.register(VJ, VJAdmin)
admin.site.register(URL, URLAdmin)

