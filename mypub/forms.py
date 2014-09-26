from django import forms


FIELD_CHOICES = (('ti','Title'),('au','Author'),
		('ab','Abstract'),('yr','Year'))
DIR_CHOICES = (('asc','Ascending'),('desc','Descending'))

class SearchForm(forms.Form):
	Keyword = forms.CharField(label='',max_length=20)

class SortForm(forms.Form):
	SortField = forms.ChoiceField(label='',choices=FIELD_CHOICES)
	SortDir = forms.ChoiceField(label='',choices=DIR_CHOICES)

