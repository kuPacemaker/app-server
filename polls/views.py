# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import User

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'polls/index.html'

def zero_ssl(request, filename):
    fsock = open(filename, "rb")
    return HttpResponse(fsock, content_type='text/plain')
