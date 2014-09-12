#from django.shortcuts import render

# Create your views here.

from mypub.models import *
from django.http import HttpResponse
from django.template import RequestContext, loader

def index(request):
	all_list = Publication.objects.order_by('Year')
	template = loader.get_template('mypub/index.html')
	context = RequestContext(request, {'all_list': all_list})
	return HttpResponse(template.render(context))

def detail(request, mypub_id):
	paper = Publication.objects.get(id=mypub_id)
        template = loader.get_template('mypub/detail.html')
        context = RequestContext(request, {'paper': paper})
        return HttpResponse(template.render(context))
