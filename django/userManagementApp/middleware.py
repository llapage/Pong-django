from django.utils import timezone
from .models import PlayerProfile
from django.contrib.auth.models import User
from django.db import transaction

class UserActivityMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)
		
		if request.user.is_authenticated:
			try: #necessaire parce que user n'a pas tout de suite un playerprofile
				with transaction.atomic():
					profile = request.user.profile
					profile.is_online = True
					profile.last_activity = timezone.now()
					profile.save(update_fields=['is_online', 'last_activity'])
			
			except PlayerProfile.DoesNotExist:
				return response
		return response