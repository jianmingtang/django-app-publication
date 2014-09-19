from django.http import HttpResponse
from django.template import RequestContext, loader

def index(request):
	template = loader.get_template('index.html')
	context = RequestContext(request, {})
	return HttpResponse(template.render(context))


#from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render

def contact(request):
    errors = []
    if request.method == 'POST':
        if not request.POST.get('subject', ''):
            errors.append('Enter a subject.')
        if not request.POST.get('message', ''):
            errors.append('Enter a message.')
        if request.POST.get('email') and '@' not in request.POST['email']:
            errors.append('Enter a valid e-mail address.')
        if not errors:
            print request.POST['subject'], request.POST['message'], \
		request.POST['email']
#                request.POST.get('email', 'noreply@example.com'),
#                ['siteowner@example.com'],
#            )
            return HttpResponseRedirect('/contact/thanks/')
    return render(request, 'contact_form.html',
        {'errors': errors})
