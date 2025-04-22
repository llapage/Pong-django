from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import PlayerProfile
import magic
import json
import os
from django.conf import settings
from .utils import userDataErrorFinder
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProfilePictureSerializer
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
@csrf_exempt
def log(request):
	if (request.method == 'POST'):
		data = json.loads(request.body)
		username = data.get('username')
		password = data.get('password')
		if (username == 'AI' or username == 'django_superuser'):
			return JsonResponse({'username': 'unauthorized'}, status=202)
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return JsonResponse({'message': 'User logged in.'}, status=200)
		elif User.objects.filter(username=username).exists():
			return JsonResponse({'password': 'invalid'}, status=202)
		else:
			return JsonResponse({'username': 'invalid'}, status=202)

@login_required
def log_out(request):
	if request.user.is_authenticated:
		logout(request)
		return JsonResponse({'message': 'User logged out.'}, status=200)
	return JsonResponse({'message': 'User not authenticated in the first place'}, status=400)

def auth(request):
	if request.user.is_authenticated:
		return JsonResponse({'authenticated': True}, status=200)
	else:
		return JsonResponse({'authenticated': False}, status=200) # change this to 200 and adapt the js response

@csrf_exempt
def register(request):
	data = json.loads(request.body)
	# Check format and duplicates
	dataErrors = userDataErrorFinder(data)
	if bool(dataErrors):
		return JsonResponse(dataErrors, status=202)

	# Create the user
	user = User.objects.create_user(
		username=data.get('username'),
		email=data.get('email'),
		password=data.get('password')
	)
	if user is None:
		return JsonResponse({'message': 'Error on user creation.'}, status=500)
	login(request, user)
	return JsonResponse({'message': 'User account created.'}, status=200)

@login_required
def getProfile(request, userId=None):
	if userId == None:
		user = request.user
	else:
		user, created = User.objects.get_or_create(id=userId)
		if created:
			user.delete()
			return JsonResponse({"error": "Profile not found"}, status=404)
	try:
		profile = user.profile  # Directly access OneToOneField (always lowercase)
	except PlayerProfile.DoesNotExist:
		return JsonResponse({"error": "Profile not found"}, status=404)
	
	#static/html/profile.html
	#static/js/profilePage.js
	profile_data = {
		"username": user.username,
		"email": user.email,
		"nickname": profile.nickname,
		"id": str(user.id),
		"wins": str(profile.wins),
		"losses": str(profile.losses),
		"ratio": str(round(profile.wins / (profile.wins + profile.losses), 2)) if profile.losses != 0 else str(profile.wins)
		# other user data fields
	}

	return JsonResponse(profile_data, status=200)

@login_required
@transaction.atomic
def profileUpdate(request):
	if request.method == "POST":
		data = json.loads(request.body)
		dataErrors = userDataErrorFinder(data) #no argv since json contains strictly only modified user data fields
		if bool(dataErrors):
			return JsonResponse(dataErrors, status=202)

		# Update user details
		user = request.user
		profile = user.profile
		# static/js/profilePage.js
		for key, arg in data.items():
			match key:
				case "username":
					user.username = arg
				case "email":
					user.email = arg
				case "nickname":
					profile.nickname = arg
				case "password":
					user.set_password(arg)
				case _:
					print("profileUpdate() data anomaly: key={}, arg={}".format(key, arg))
		user.save(update_fields=['username', 'email', 'password'])
		profile.save(update_fields=['nickname'])
		return JsonResponse(data, status=200)
	return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@transaction.atomic
def set_profile_pic(request):
	profile = request.user.profile
	if request.method == "DELETE":
		profile.profile_picture.delete(save=False)
		profile.profile_picture = None
		profile.save(update_fields=['profile_picture'])
		return JsonResponse({'success': 'Deleted profile picture'}, status=200)
	if 'image' not in request.FILES:
		return JsonResponse({'error': 'No image file provided'}, status=400)
	
	image_file = request.FILES['image']
	
	if image_file.size > settings.MAX_UPLOAD_SIZE:
		return JsonResponse({'error': f"File size exceeds maximum allowed ({settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB)"},
							status=400)
	
	mime = magic.Magic(mime=True) #file type detector
	file_type = mime.from_buffer(image_file.read(1024)) #detect file type from head
	image_file.seek(0) #reset reading pointer
	if file_type not in settings.ALLOWED_IMAGE_TYPES:
		return JsonResponse({'error': f'Invalid file type. Allowed types: {", ".join(settings.ALLOWED_IMAGE_TYPES)}'},
							status=400)

	if profile.profile_picture and os.path.isfile(profile.profile_picture.path): #if user already has profile pic
		os.remove(profile.profile_picture.path)
	profile.profile_picture.save(image_file.name, image_file) # will call model's set_profile_image_path and store image
	profile.save(update_fields=['profile_picture'])

	serializer = ProfilePictureSerializer(profile)
	return JsonResponse(serializer.data, status=200)

@login_required
def get_profile_pic(request, userId):
	try:
		user = User.objects.get(id=userId)
		serializer = ProfilePictureSerializer(user.profile)
		return JsonResponse(serializer.data, status=200)
	except User.DoesNotExist:
		return JsonResponse({"error": "User not found"}, status=404)


@login_required
def getNames(requset, userId):
	try:
		user = User.objects.get(id=userId)
		return JsonResponse({'id': userId, 'username': user.username, 'nickname': user.profile.nickname}, status=200)
	except User.DoesNotExist:
		return JsonResponse({'error': 'user not found'}, status=404)