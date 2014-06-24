from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	cid = models.OneToOneField(User) #username
	name = models.CharField(max_length=100, blank=True)


	def get_display_name(self):
		if self.name:
			return self.name
		return self.user.username

	def __unicode__(self):
		return self.user.username

