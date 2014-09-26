from django.shortcuts import render

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.db.models import Q
from mypub.models import Article, Journal, URL, VJ
from mypub.forms import SearchForm,SortForm
import re



def to_full_vj_name(vlist):
	vjlist = {
		'\\VJAS': 'Applications of Superconductivity',
		'\\VJNST': 'Nanoscale Science and Technology',
		'\\VJQI': 'Quantum Information',
	}
	for v in vlist:
		if v.title in vjlist:
			v.title = 'Virtual Journal of ' + vjlist[v.title]
	return vlist

def to_html(s):
	s = re.sub(r'\$(.*?)_{(.*?)}(.*?)\$', r'$\1<sub>\2</sub>\3$',s)
	s = re.sub(r'\$(.*?)\^{(.*?)}(.*?)\$', r'$\1<sup>\2</sup>\3$',s)
	s = re.sub(r'\$(.*?)\$', r'<i>\1</i>',s)
	s = s.replace('\\bar{1}',
		'<span style="text-decoration: overline">1</span>')
	s = s.replace('\\delta','<math><mi>&delta;</mi></math>')
	s = s.replace('\\AA{}','&Aring;')
	s = s.replace('\\%','%')
	s = s.replace(u'\u00e9','&eacute;')
	s = s.replace(u'\u00c7','&Ccedil;')
	return s

def get_all_extra_links(a):
	ul = URL.objects.filter(article_id=a.id).order_by('id')
	vl = VJ.objects.filter(article_id=a.id).order_by('id')
	vl = to_full_vj_name(vl)
	return ul, vl

def get_thumb_name(ulist):
	for u in ulist:
		if u.name == '[Full Text]':
			t = u.link.replace('pdf','png')
	return t

def get_one_paper_from_aid(aid):
	a = Article.objects.get(id=aid)
	j = Journal.objects.get(id=a.journal_id)
	a.title = to_html(a.title)
	a.author = to_html(a.author)
	a.abstract = to_html(a.abstract)
	ulist, vlist = get_all_extra_links(a)
	t = get_thumb_name(ulist)
	return a, j, ulist, vlist, t

def field(x):
	return {'ti': x[0].title,    'au': x[0].author,
		'ab': x[0].abstract, 'yr': x[1].year, }

def sort_plist(plist,sortf,sortd):
	if sortd == 'desc':
		rev = True
	else:
		rev = False
	plist.sort(key = lambda x: field(x)[sortf], reverse=rev)

def get_sort_form(request):
	if 'SortField' in request.GET:
		soform = SortForm(request.GET)
	else:
		soform = SortForm()
	return soform

def process_sort_form(soform,plist):
	if soform.is_valid():
		sortf = soform.cleaned_data['SortField']
		sortd = soform.cleaned_data['SortDir']
		sort_plist(plist,sortf,sortd)

def index(request):
	alist = Article.objects.order_by('-journal__year')
	plist = []
	for a in alist:
		plist.append(get_one_paper_from_aid(a.id))
	seform = SearchForm()
	soform = get_sort_form(request)
	process_sort_form(soform,plist)
	template = loader.get_template('mypub/index.html')
	context = RequestContext(request, {'plist': plist,
		'searchform': seform, 'sortform': soform})
	return HttpResponse(template.render(context))

def detail(request, aid):
	paper = get_one_paper_from_aid(aid)
	template = loader.get_template('mypub/detail.html')
	context = RequestContext(request, {'paper': [paper]})
	return HttpResponse(template.render(context))

def search(request):
	seform = SearchForm(request.GET)
	if seform.is_valid():
		kw = seform.cleaned_data['Keyword']
		slist = kw.split()
		request.session['Keyword'] = kw
		request.session.set_expiry(300)
		message = 'Searched for (%r),' % kw
	else:
		kw = request.session.get('Keyword')
		if kw:
			message = message = 'Searched for (%r),' % kw
			slist = kw.split()
		else:
			slist = []
			message = 'Your keyword is invalid,'
	q = Q()
	for sub in slist:
		q = q & ( Q(title__icontains=sub) \
		| Q(author__icontains=sub) | Q(abstract__icontains=sub) )
	if slist:
		alist = Article.objects.filter(q).order_by('-journal__year')
	else:
		alist = []
	message = message + ' and returned %d records.' % len(alist)
	plist = []
	for a in alist:
		plist.append(get_one_paper_from_aid(a.id))
	soform = get_sort_form(request)
	process_sort_form(soform,plist)
	template = loader.get_template('mypub/index.html')
	context = RequestContext(request, {'plist': plist, 'msg': message,
		'searchform': seform, 'sortform': soform})
	return HttpResponse(template.render(context))
