from dataclasses import dataclass, field
import asyncio

from channels.layers import get_channel_layer # type: ignore

@dataclass
class User:
	nickname: str
	channel_name: str
	inputs: list[dict]
	timeout_task: asyncio.Task = None
	missing: bool = False
	channel_group_name: list = field(default_factory=list)
	game_constant: any = None
	in_game: bool = False
	in_tournament: bool = False
	game_stop_function: any = None
	top_bot: bool = False


class Users:
	_users = {}
	_channel_layer = get_channel_layer()

	@classmethod
	def get(cls, user_id: str):
		return cls._users.get(user_id)

	@classmethod
	def is_in_game(cls, user_id: str):
		user = cls._users.get(user_id)
		if user:
			return user.in_game
		return False

	@classmethod
	def is_in_tournament(cls, user_id: str):
		user = cls._users.get(user_id)
		if user:
			return user.in_tournament
		return False

	@classmethod
	def append(cls, user_id: str, consumer_user):
		if not cls.get(user_id):
			cls._users[user_id] = User(
				nickname=consumer_user.nickname,
				channel_name=consumer_user.channel_name,
				inputs=[consumer_user.inputs],
			)

	@classmethod
	def remove(cls, user_id: str):
		cls._users.pop(user_id, None)

	async def _time_out(self, user_id: str, user: User):
		time = 5
		while time != 0:
			time -= 1
			await asyncio.sleep(1)
			if not user.missing:
				return
		if user.in_game and user.game_stop_function:
			await user.game_stop_function(user_id)
		Users.remove(user_id)

	@classmethod
	async def disconnect(cls, user_id: str):
		user = cls.get(user_id)
		if user and (user.in_game or user.in_tournament):
			user.missing = True
			user.timeout_task = asyncio.create_task(cls._time_out(cls, user_id, user))
			for name in user.channel_group_name:
				await cls._channel_layer.group_discard(name, user.channel_name)

	@classmethod
	async def reconnect(cls, user_id: str, consumer_user):
		user = cls.get(user_id)
		if user and user.missing:
			user.missing = False
			user.channel_name = consumer_user.channel_name
			user.inputs.clear()
			user.inputs.append(consumer_user.inputs)
			if user.in_game:
				await cls._channel_layer.send(
					user.channel_name,
					{
						"type": "msg",
						"event": "game",
						"constant": user.game_constant
					}
				)
				await cls._channel_layer.send(user.channel_name, {"type": "msg", "event": "start",})
				for name in user.channel_group_name:
					await cls._channel_layer.group_add(name, user.channel_name)
			elif user.in_tournament:
				await cls._channel_layer.send(
					user.channel_name,
					{
						"type": "msg",
						"event": "waiting_room",
					}
				)





# from dataclasses import dataclass
# import asyncio

# @dataclass
# class User:
# 		nickname: str
# 		channel_name: str
# 		keys: dict[bool, bool]
# 		timeout_task: asyncio.Task = None
# 		missing = False
# 		game_constant = None


# class Connections:
# 	_active_connections = []
# 	_active_games = {}
# 	_users_info = {}

# 	@classmethod
# 	def is_in_game(cls, id):
# 		return cls._active_games.get(id)

# 	@classmethod
# 	def is_in_active_connections(cls, id):
# 		return id in cls._active_connections

# 	@classmethod
# 	def add_to_active_connections(cls, id, user):
# 		if not cls.is_in_game(id) and id not in cls._active_connections:
# 			cls._active_connections.append(id)
# 			cls._users_info[id] = User(
# 				nickname=user.nickname,
# 				channel_name=user.channel_name,
# 				keys=user.keys,
# 			)

# 	@classmethod
# 	def rmv_from_active_connections(cls, id):
# 		if id in cls._active_connections:
# 			cls._active_connections.remove(id)
# 			cls._users_info.pop(id, None)

# 	@classmethod
# 	def add_to_game(cls, id, game):
# 		if id in cls._active_connections:
# 			cls.rmv_from_active_connections(id)
# 		if not cls._active_games.get(id):
# 			cls._active_games[id] = game
# 			cls.get_user_info(id).game_constant = game.pong.get_game_constant()

# 	@classmethod
# 	def rmv_from_game(cls, id):
# 		if cls._active_games.get(id):
# 			del cls._active_games[id]
# 			user = cls._users_info.pop(id, None)
# 			if user.timeout_task and not user.timeout_task.cancelled():
# 				user.event.set()

# 	@classmethod
# 	def get_user_info(cls, id):
# 		return cls._users_info.get(id)

# 	async def _time_out(cls, id, user):
# 		time = 10
# 		while time != 0:
# 			if not user.missing:
# 				return
# 			time -= 1
# 			await asyncio.sleep(1)
# 		cls.rmv_from_game(id)

# 	@classmethod
# 	async def disconnect(cls, id):
# 		game = cls._active_games.get(id)
# 		user = cls._users_info.get(id)
# 		if game and user:
# 			user.keys['ArrowDown'] = False
# 			user.keys['ArrowUp'] = False
# 			user.missing = True
# 			user.timeout_task = asyncio.create_task(cls._time_out(id, user))
# 			await game.rmv_user_from_group(user.channel_name)

# 	@classmethod
# 	async def reconnect(cls, id, consumer):
# 		game = cls._active_games.get(id)
# 		user = cls._users_info.get(id)
# 		if user and game and user.timeout_task and not user.timeout_task.cancelled():
# 			user.missing = False
# 			await user.msg({'event': 'Game', 'constant': user.game_constant})
# 			user.channel_name = consumer.channel_name
# 			user.keys = consumer.keys
# 			await game.add_user_from_group(user.channel_name)
