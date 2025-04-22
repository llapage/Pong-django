from django.shortcuts import render, HttpResponse
from .models import Game
from userManagementApp.models import PlayerProfile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

def gamePlayerErrFind(userId):
	if not User.objects.filter(id=userId).exists():
		return "user id not found"
def gameDataErrorFinder(data):
	responseObj = {}
	error = ""
	for userId in data.keys():
		error = gamePlayerErrFind(userId)
		if error:
			responseObj[userId] = error
	return responseObj

@transaction.atomic
def save_game(data, game_type='classic'): #{uid_player1: score, uid_player2: score}
	dataErrors = gameDataErrorFinder(data)
	if bool(dataErrors):
		return JsonResponse(dataErrors, status=401)
	game = Game.objects.create(scores=data, game_type=game_type, creation=datetime.now() + timedelta(hours=2))
	winner = game.getWinner()
	for key, value in data.items():
		game.players.add(PlayerProfile.objects.get(user__id=key))
		profile = PlayerProfile.objects.get(user__id=key)
		if str(key) == str(winner):
			profile.wins += 1
		else:
			profile.losses += 1
		profile.save(update_fields=['wins', 'losses'])
	return JsonResponse({'success': 'saved it perfecty'}, status=300)

@login_required
def get_games(request, targetUserId=None):
	try:
		user = request.user if targetUserId == None else User.objects.get(id=targetUserId)
		games = user.profile.game_history.all()
		gamesJSON = {}
		for game in games:
			game_data = {
				'datetime': game.creation.strftime('%d %B %Y - %H:%M'),
				'game_type': game.game_type,
				'players': [
					{
						'id': str(player.id),
						'username': str(player.user.username),
						'nickname': str(player.nickname),
						'score': str(game.getScore(str(player.id)))
					}
					for player in game.players.all()
				],
				'winner': str(game.getWinner()),
				'request': str(request.user.id),
			}
			gamesJSON[str(game.id)] = game_data
		if bool(gamesJSON):
			return JsonResponse(gamesJSON, status=200)
		else:
			return JsonResponse({'warning': 'no game history found'}, status=201)
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)

def save_fake_game(request):
	data = {
		'3': 12,
		'4': 7
	}
	return save_game(data)
