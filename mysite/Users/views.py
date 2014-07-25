from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.template.response import TemplateResponse

from Users.models import UserProfile

def index(request):
    #return HttpResponse("Welcome to Flite.")
    return TemplateResponse(request, 'Users/index.html')
