#from django.shortcuts import render

from mypub.models import *
from django.http import HttpResponse
from django.template import RequestContext, loader
import re

vjlist = { '0' : 'Virtual Journal of ',
        '\\VJAS': 'Applications of Superconductivity',
        '\\VJNST': 'Nanoscale Science and Technology',
        '\\VJQI': 'Quantum Information',
        }
vjlist_keys = vjlist.keys()

def fix_HTML(s):
	s = re.sub(r'\$(.*?)_{(.*?)}(.*?)\$', r'$\1<sub>\2</sub>\3$',s)
	s = re.sub(r'\$(.*?)\^{(.*?)}(.*?)\$', r'$\1<sup>\2</sup>\3$',s)
	s = re.sub(r'\$(.*?)\$', r'<i>\1</i>',s)
	s = s.replace('\\bar{1}',
		'<span style="text-decoration: overline">1</span>')
	s = s.replace('\\delta','<math>&delta;</math>')
	s = s.replace('\\AA{}','&Aring;')
	s = s.replace('\\%','%')
	s = s.replace(u'\u00e9','&eacute;')
	s = s.replace(u'\u00c7','&Ccedil;')
	return s

def index(request):
	jlist = Journal.objects.order_by('-year')
	plist = []
	for j in jlist:
		a = Article.objects.filter(journal_id=j.id)[0]
		a.title = fix_HTML(a.title)
		a.author = fix_HTML(a.author)
		a.abstract = fix_HTML(a.abstract)
		ulist = URL.objects.filter(article_id=a.id).order_by('id')
		vlist = VJ.objects.filter(article_id=a.id)
		for v in vlist:
			v.title = vjlist['0'] + vjlist[v.title]
		plist.append([a,j,ulist,vlist])
	template = loader.get_template('mypub/index.html')
	context = RequestContext(request, {'plist': plist,})
	return HttpResponse(template.render(context))

def detail(request, mypub_id):
	paper = Article.objects.get(id=article_id)
        template = loader.get_template('mypub/detail.html')
        context = RequestContext(request, {'paper': paper})
        return HttpResponse(template.render(context))
