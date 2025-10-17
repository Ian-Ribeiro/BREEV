from django.db import models
from django.conf import settings


# Simple profile model linked to the project's user model.
class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	bio = models.CharField(max_length=255, blank=True, null=True)

	def __str__(self):
		return f"Profile of {self.user.username}"
