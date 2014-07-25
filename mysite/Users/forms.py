from registration.forms import RegistrationForm
from django import forms

class CustomRegistrationForm(RegistrationForm):
	first_name = forms.CharField(max_length=30)
	last_name = forms.CharField(max_length=30)