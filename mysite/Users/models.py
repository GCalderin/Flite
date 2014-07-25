from django.db import models
from django.contrib.auth.models import User
from registration.signals import user_registered

class UserProfile(models.Model):
	cid = models.ForeignKey(User, unique=True) #username
	# name = models.CharField(max_length=100)
	# email = models.CharField(max_length=100)

	def get_display_name(self):
		return self.cid.first_name

	def __unicode__(self):
		return self.cid.first_name

	def user_registered_callback(sender, user, request, **kwargs):
		profile = UserProfile(cid = user)
		user.first_name = request.POST["first_name"]
		user.last_name = request.POST["last_name"]

		profile.save()
		user.save()

	user_registered.connect(user_registered_callback)

