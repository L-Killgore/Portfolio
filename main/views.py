import os
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import Contact

# Create your views here.
def index(request):
    form = Contact(request.POST or None)

    if form.is_valid():
        form.send()
        sender = form.cleaned_data.get('name')

        messages.success(request, f"Thank you {sender}! I will respond to your message shortly.")
        redirect('main:portfolio')

    return render(request, 'main/index.html', {
        'form': form
    })

def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type = 'application/resume')
            response['Content-Disposition'] = 'inline;filename='+os.path.basename(file_path)
            return response

    raise Http404