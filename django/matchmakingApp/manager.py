from gameStatsApp.views import save_game
from .game import Game
from .users import Users
import asyncio
from asgiref.sync import sync_to_async

from channels.layers import get_channel_layer # type: ignore

class Match():

	_queue = []
	_user_data = {}
	_nb_players = 2
	_channel_layer = get_channel_layer()
	_game_type = "Classic"

	@classmethod
	async def append(cls, user_id: str, consumer):
		if user_id not in cls._queue:
			cls._queue.append(user_id)
			cls._user_data[user_id] = consumer
			await cls._check_start()

	@classmethod
	def rmv_from_queue(cls, user_id: str):
		if user_id in cls._queue:
			cls._queue.remove(user_id)
			del cls._user_data[user_id]

	@classmethod
	async def _check_start(cls):
		if len(cls._queue) >= cls._nb_players:
			players = cls._queue[:cls._nb_players]
			cls._queue = cls._queue[cls._nb_players:]
			for id in players:
				Users.append(id, cls._user_data[id])
				del cls._user_data[id]
			asyncio.create_task(cls._start(players))

	@classmethod
	async def _start(cls, users_id: list):
		game = Game(users_id)
		await game.start()
		await sync_to_async(save_game, thread_sensitive=True)(game.pong.get_result(), cls._game_type)
		await cls._channel_layer.group_send(game.game_id, {"type": "end_message", "event": "end", "result": game.pong.get_result(), "users": game.nicknames})
		for user_id in users_id:
			user = Users.get(user_id)
			if user:
				await cls._channel_layer.group_discard(user.channel_group_name[0], user.channel_name)
				Users.remove(user_id)


class Tournament(Match):

	_queue = []
	_nb_players = 4

	@classmethod
	async def _round_manager(cls, round_ids: list):
		results = []
		async with asyncio.TaskGroup() as asyncGameGroup:
			for i in range(0, len(round_ids), 2):
				asyncGameGroup.create_task(cls._play_match(round_ids[i:i+2], results))
		return results
 

	@classmethod
	async def _play_match(cls, players: list, results: list):
		p1, p2 = Users.get(players[0]), Users.get(players[1])
		if p1 and p2:
			game = Game(players)
			await game.start()
			winners = game.pong.get_winners()
			loosers = game.pong.get_loosers()
		else:
			winners = [players[0] if p1 else players[1]]
			loosers = [players[0] if p2 else players[1]]
		results.extend(winners)
		user = Users.get(winners[0])
		if user:
			await cls._channel_layer.send(user.channel_name, {
				"type": "msg",
				"event": "temporary_end",
				"result": "You passed the round.",
			})
			await cls._channel_layer.group_discard(user.channel_group_name[0], user.channel_name)
		user = Users.get(loosers[0])
		if user:
			await cls._channel_layer.send(user.channel_name, {
				"type": "end_message",
				"event": "end",
				"result": game.pong.get_result(),
				"users": game.getNickname(),
			})
			await cls._channel_layer.group_discard(user.channel_group_name[0], user.channel_name)
			Users.remove(loosers[0])
  
	@classmethod
	async def _start(cls, tournament_ids: list):
		for user_id in tournament_ids:
			user = Users.get(user_id)
			if user:
				user.in_tournament = True
		while len(tournament_ids) > 1:
			tournament_ids = await cls._round_manager(tournament_ids)
		winner = tournament_ids.pop()
		user = Users.get(winner)
		if user:
			await cls._channel_layer.send(user.channel_name, {
				"type": "end_message",
				"event": "end",
				"result": "YOU WON THE TOURNAMENT !",
			})
			Users.remove(winner)



class Multiplayer(Match):

	_queue = []
	_nb_players = 4
	_game_type = "Multiplayers"

class MatchVsIA(Match):

	_queue = []
	_nb_players = 1
	_game_type = "AI"


class Clash(Match):

	_queue = {}
	_user_data = {}
	_channel_layer = get_channel_layer()
	_game_type = "Challenge"

	@classmethod
	async def append(cls, user_id: str, game_id: str, consumer):
		if game_id not in cls._queue:
			cls._queue[game_id] = user_id
			cls._user_data[user_id] = consumer
		else:
			p1_id = cls._queue[game_id]
			players = [p1_id, user_id]
			Users.append(user_id, consumer)
			Users.append(p1_id, cls._user_data[p1_id])
			del cls._queue[game_id]
			del cls._user_data[p1_id]
			asyncio.create_task(cls._start(players))
			# await cls._check_start()

