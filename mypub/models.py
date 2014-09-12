from django.db import models

class Article(models.Model):
	def __unicode__(self):
		return self.Title
	Title = models.CharField(max_length=200)
	Author = models.CharField(max_length=200)
	Journal = models.CharField(max_length=50)
	Volume = models.CharField(max_length=10)
	Page = models.CharField(max_length=10)
	Year = models.IntegerField()
	Link = models.URLField()
	Local = models.URLField()
	Abstract = models.CharField(max_length=1500)
	Note = models.CharField(max_length=100)

class ConfPaper(models.Model):
	def __unicode__(self):
		return self.Title
	Title = models.CharField(max_length=200)
	Author = models.CharField(max_length=200)
	Meeting = models.CharField(max_length=50)
	Address = models.CharField(max_length=50)
	Date = models.DateTimeField()
	Abstract = models.CharField(max_length=1500)
	Note = models.CharField(max_length=100)
