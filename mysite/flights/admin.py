from django.contrib import admin
from flights.models import *

class PersonalAdmin(admin.ModelAdmin):
	search_fields = ('')
