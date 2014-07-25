from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from Users import views

urlpatters = patterns('', 
	url (r'^index$', 'Users.views.index', name='index'),
	)