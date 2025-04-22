from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from .models import FriendRequest
from userManagementApp.models import PlayerProfile
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

@login_required
def invite(request, targetUserId):
	try:
		if targetUserId == request.user.id:
			return JsonResponse({"error": 'You cannot invite yourself'}, status=400) 
		to_user = User.objects.get(id=targetUserId)
		friend_request_dupplicate = FriendRequest.objects.filter(
			from_user=request.user, to_user=to_user
		).exists()
		if friend_request_dupplicate:
			return JsonResponse({"error": 'Friend request has already been created and sent'}, status=204)
		if to_user.profile.blocked.filter(id=request.user.id).exists():
			return JsonResponse({"error": 'The target user has blocked you'}, status=301)
		with transaction.atomic():
			friend_request = FriendRequest.objects.create(
				from_user=request.user, to_user=to_user
			)
		return JsonResponse({
			"success": 'Created and sent friend request',
			"request_id": friend_request.id
		}, status=200)
	except User.DoesNotExist:
		return JsonResponse({"error": 'Target user doesn\'t exist'}, status=204)

@login_required
def remove(request, targetUserId):
	try:
		to_user = User.objects.get(id=targetUserId)
		with transaction.atomic():
			request.user.profile.friends.remove(to_user.profile)
		return JsonResponse({
			"success":f'Removed user {targetUserId} from {request.user.id}\'s friends list'
		}, status=200)
	except User.DoesNotExist:
		return JsonResponse({"error": 'Target user doesn\'t exist'}, status=204)

@login_required
def block(request, targetUserId):
	try:
		targetUser = User.objects.get(id=targetUserId)
		if targetUserId == request.user.id:
			return JsonResponse({"error": 'You cannot block yourself'}, status=400) 
		with transaction.atomic():
			if targetUser.profile in request.user.profile.friends.all():
				request.user.profile.friends.remove(targetUser.profile)
			request.user.profile.blocked.add(targetUser.profile)

			FriendRequest.objects.filter(from_user=request.user, to_user=targetUser).delete()
			FriendRequest.objects.filter(to_user=request.user, from_user=targetUser).delete()
	
		return JsonResponse({
			"success":f'Blocked user {targetUserId} from {request.user.id}\'s profile'
		}, status=200)
	except User.DoesNotExist:
		return JsonResponse({"error": 'Target user doesn\'t exist'}, status=204) 

@login_required
def unblock(request, targetUserId):
	try:
		targetUser = User.objects.get(id=targetUserId)
		with transaction.atomic():
			request.user.profile.blocked.remove(targetUser.profile)
		return JsonResponse({
			"success":f'Removed user {targetUserId} from {request.user.id}\'s blocked list'
		}, status=200)
	except User.DoesNotExist:
		return JsonResponse({"error": 'Target user doesn\'t exist'}, status=204)

@login_required
def accept(request, requestId): #id of FriendRequest instance
	try:
		with transaction.atomic():
			fRequest = FriendRequest.objects.select_for_update().get(id=requestId)

			if fRequest.to_user != request.user or fRequest.to_user.profile.blocked.filter(id=fRequest.from_user.id).exists() or fRequest.from_user.profile.blocked.filter(id=fRequest.to_user.id).exists():
				return JsonResponse({"error": 'Unauthorized friend request'}, status=403)
			fRequest.to_user.profile.friends.add(fRequest.from_user.profile)
			#fRequest.from_user.profile.friends.add(fRequest.to_user.profile) #symetrical
			fRequest.delete()
		return JsonResponse({"success": 'Friend request accepted'}, status=200)

	except FriendRequest.DoesNotExist:
		return JsonResponse({"error": "FriendRequest not found"}, status=204)


@login_required
def reject(request, requestId):
	try:
		with transaction.atomic():
			friend_request = FriendRequest.objects.select_for_update().get(id=requestId)

			if friend_request.to_user != request.user and friend_request.from_user != request.user:
				return JsonResponse({"error": 'Unauthorized friend request'}, status=403)
			friend_request.delete()
			return JsonResponse({"success": 'Friend request rejected'}, status=200)
	except FriendRequest.DoesNotExist:
		return JsonResponse({"error": "FriendRequest not found"}, status=204)

@login_required
def getOnlinePlayers(request):
	updateOnlineStatus()
	connected_users = User.objects.filter(
		profile__is_online=True,
	).exclude(id=request.user.id)
	return JsonResponse({
		str(user.id): user.profile.nickname
		for user in connected_users
	})

@login_required
def getOnlineFriends(request):
	updateOnlineStatus()
	connected_profiles = request.user.profile.friends.filter(
		user__profile__is_online=True
	).exclude(user=request.user)
	return JsonResponse({
		str(profile.user.id): profile.nickname
		for profile in connected_profiles
	})

@login_required
def getFriends(request):
	friends = request.user.profile.friends.all()
	return JsonResponse({
		str(friend.user.id): friend.nickname
		for friend in friends
	})

@login_required
def getBlockedUsers(request):
	blockedUsers = request.user.profile.blocked.all()
	return JsonResponse({
		str(blockedUser.user.id): blockedUser.nickname
		for blockedUser in blockedUsers
	})

@login_required
def getOnlineStrangers(request):
	updateOnlineStatus()
	friend_ids = request.user.profile.friends.values_list('user_id', flat=True)
	blocked_ids = request.user.profile.blocked.values_list('user_id', flat=True)
	# blocked_by_ids = User.objects.filter(
    #     profile__blocked=request.user.profile	#Uncomment to make block-behaviour more strict
    # ).values_list('id', flat=True)
	connected_strangers = User.objects.filter(
		profile__is_online=True,
	).exclude(id__in = [request.user.id] + list(friend_ids) + list(blocked_ids))# + list(blocked_by_ids))

	
	return JsonResponse({
		str(user.id): user.profile.nickname
		for user in connected_strangers
	})


@login_required
def inFriendRequests(request):
	Requests = FriendRequest.objects.filter(to_user=request.user)
	invites = {}
	for req in Requests:
		from_user = {
			"username": req.from_user.profile.nickname, 
			"userId": req.from_user.id
		}
		invites[str(req.id)] = from_user
	return JsonResponse(invites, status=200)

def updateOnlineStatus():
	threshold = timezone.now() - timedelta(minutes=1)
	count = PlayerProfile.objects.filter(
		is_online=True, 
		last_activity__lt=threshold
	).update(is_online=False)

@login_required
def is_blocked(request, targetUserId):
	return JsonResponse({'is_blocked': True if request.user.profile.blocked.filter(id=targetUserId).exists() else False
	}, status=200)
	
@login_required
def social_status(request, targetUserId):
	if request.user.id == targetUserId:
		return JsonResponse({'error': 'Unauthorized introspection'}, status=300)
	inFrRequest = -1
	if FriendRequest.objects.filter(to_user=request.user, from_user=targetUserId).exists():
		inFrRequest = FriendRequest.objects.get(to_user=request.user, from_user=targetUserId).id
	outFrRequest = -1
	if FriendRequest.objects.filter(to_user=targetUserId, from_user=request.user).exists():
		outFrRequest = FriendRequest.objects.get(to_user=targetUserId, from_user=request.user).id
	return JsonResponse({
		"is_blocked": True if request.user.profile.blocked.filter(id=targetUserId).exists() else False,
		"blocked_me": True if User.objects.filter(id=targetUserId).exists() and User.objects.get(id=targetUserId).profile.blocked.filter(id=request.user.id).exists() else False,
		"is_friend": True if request.user.profile.friends.filter(id=targetUserId).exists() else False,
		"is_inviting": inFrRequest,
		"was_invited": outFrRequest,
	}, status=200 )

def are_friends(uID1, uID2):
	try:
		user1 = User.objects.get(id=uID1)
		return user1.profile.friends.filter(id=uID2).exists()
	except User.DoesNotExist:
		return False