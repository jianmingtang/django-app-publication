from django.shortcuts import render

from django.http import HttpResponse
from django.template import RequestContext, loader
from mypub.models import Article, Journal, URL, VJ
import re

vjlist = { '0' : 'Virtual Journal of ',
        '\\VJAS': 'Applications of Superconductivity',
        '\\VJNST': 'Nanoscale Science and Technology',
        '\\VJQI': 'Quantum Information',
        }
vjlist_keys = vjlist.keys()

def toFullName(vlist):
	for v in vlist:
		v.title = vjlist['0'] + vjlist[v.title]
	return vlist

def toHTML(s):
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

def extract_one_article(a):
	a.title = toHTML(a.title)
	a.author = toHTML(a.author)
	a.abstract = toHTML(a.abstract)
	ul = URL.objects.filter(article_id=a.id).order_by('id')
	vl = VJ.objects.filter(article_id=a.id).order_by('id')
	vl = toFullName(vl)
	return a, ul, vl

def get_thumb_name(ulist):
	for u in ulist:
		if u.name == '[Full Text]':
			t = u.link.replace('pdf','png')
	return t

def index(request):
	jlist = Journal.objects.order_by('-year')
	plist = []
	for j in jlist:
		a = Article.objects.filter(journal_id=j.id)[0]
		a, ulist, vlist = extract_one_article(a)
		t = get_thumb_name(ulist)
		plist.append([a,j,ulist,vlist,t])
	template = loader.get_template('mypub/index.html')
	context = RequestContext(request, {'plist': plist})
	return HttpResponse(template.render(context))

def detail(request, aid):
	a = Article.objects.get(id=aid)
	j = Journal.objects.get(id=a.journal_id)
	a, ulist, vlist = extract_one_article(a)
	t = get_thumb_name(ulist)
	paper = [a, j, ulist, vlist, t]
        template = loader.get_template('mypub/detail.html')
        context = RequestContext(request, {'paper': [paper]})
        return HttpResponse(template.render(context))
