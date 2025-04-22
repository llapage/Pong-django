from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from userManagementApp.models import PlayerProfile
from django.core.exceptions import ObjectDoesNotExist
from socialApp.views import are_friends

@login_required
def get_room(request, targetUserId):
	try:
		to_user = User.objects.get(id=targetUserId)
		from_user = request.user
		to_user_data = {
			'id': to_user.id,
			'nickname': to_user.profile.nickname,
			'email': to_user.email,
		}
		from_user_data = {
			'id': from_user.id,
			'nickname': from_user.profile.nickname,
			'email': from_user.email,
		}
		if not are_friends(from_user.id, to_user.id) :
			return JsonResponse({'error': 'Target not friend'}, status=404)
		return JsonResponse({'user_1': from_user_data, 'user_2': to_user_data}, status=200) #pour le debug
	except User.DoesNotExist:
		return JsonResponse({'error': 'Target user not found'}, status=404)


@login_required
def friends(request, friendsID):
	try:
		user1 = User.objects.get(id=request.user.id)
		if user1.profile.friends.filter(id=friendsID).exists():
			return JsonResponse({'friendship': True}, status=200)
		else:
			return JsonResponse({'friendship': False}, status=200)
	except User.DoesNotExist:
		return JsonResponse({'friendship': False}, status=200)
	