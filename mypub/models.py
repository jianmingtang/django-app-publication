from django.db import models

class Journal(models.Model):
	def __unicode__(self):
		return self.title
	title = models.CharField(max_length=200)
	volume = models.CharField(max_length=10)
	page = models.CharField(max_length=20)
	year = models.IntegerField()
	link = models.URLField()

class Article(models.Model):
	def __unicode__(self):
		return self.title
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=200)
	abstract = models.CharField(max_length=2000)
	journal = models.OneToOneField(Journal)

class VJ(models.Model):
	def __unicode__(self):
		return self.title
	title = models.CharField(max_length=200)
	volume = models.CharField(max_length=10)
	issue = models.CharField(max_length=10)
	year = models.IntegerField()
	article = models.ForeignKey(Article)

class URL(models.Model):
	def __unicode__(self):
		return self.name
	name = models.CharField(max_length=200)
	link = models.URLField()
	article = models.ForeignKey(Article)

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
