from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
import json

from .manager import Match, Tournament, Multiplayer, MatchVsIA, Clash
from .users import Users
# from userManagementApp.models import PlayerProfile
# from django.contrib.auth.models import User
from django.utils import timezone
from channels.db import database_sync_to_async # type: ignore
# from asgiref.sync import sync_to_async

class Consumer(AsyncWebsocketConsumer):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.nickname = None
		self.inputs = {'ArrowDown': False, 'ArrowUp': False}
		self.manager = None
		self.id = None
		self._actions = {
			"input": self._input,
			# "deconnected": self._disconnect,
			"give_up": self._giveUp,
			# "quit": self._quitQueue,
			"quit": self._quit,
		}
		self.user = None

	@database_sync_to_async
	def get_user_nickname(self, user):
		return user.profile.nickname

	@database_sync_to_async
	def update_activity(self, user):
		profile = user.profile
		profile.is_online = True
		profile.last_activity = timezone.now()
		profile.save(update_fields=['is_online', 'last_activity'])

	async def connect(self):
		self.user = self.scope['user']
		if self.user.is_anonymous:
			return
		await self.accept()
		# profile = self.scope['profile']
		await self.update_activity(self.user)
		self.id = self.user.id
		if Users.get(self.id):
			await Users.reconnect(self.id, self)
		else:
			self.nickname = await self.get_user_nickname(self.user)
			action = self.scope['url_route']['kwargs']['action']
			param = self.scope['url_route']['kwargs'].get('param')
			if param and action != 'clash':
				self.close()
			match action:
				case 'classique':
					self.manager = Match
					await Match.append(self.id, self)
				case 'tournament':
					self.manager = Tournament
					await Tournament.append(self.id, self)
				case 'multiplayer':
					self.manager = Multiplayer
					await Multiplayer.append(self.id, self)
				case 'ia':
					self.manager = MatchVsIA
					await MatchVsIA.append(self.id, self)
				case 'clash':
					await Clash.append(self.id, param, self)
	
	async def msg(self, event):
		event_data = event.copy()
		event_data.pop('type', None)
		try:
			await self.send(text_data=json.dumps({'event': event_data}))
		except Exception as e:
			pass
	
	async def end_message(self, event):
		try:
			event_data = event.copy()
			event_data.pop('type', None)
			await self.send(text_data=json.dumps({'event': event_data}))
		except Exception as e:
			pass
		await self.close()
	
	async def _input(self, messsage):
		dic = {'keydown': True, 'keyup': False}
		arrow_topbot = {'ArrowRight': 'ArrowDown', 'ArrowLeft': 'ArrowUp'}

		user = Users.get(self.id)
		if user and user.in_game:
			arrow_type = messsage.get('key')
			move = messsage.get('bool')
			if arrow_type and move:
				if user.top_bot:
					if arrow_type in arrow_topbot:
						self.inputs[arrow_topbot[arrow_type]] = dic[move]
				else:
					self.inputs[arrow_type] = dic[move]

	async def _giveUp(self, messsage):
		user = Users.get(self.id)
		if user and (user.in_game or user.in_tournament):
			await user.game_stop_function(self.id)
			Users.remove(self.id)
 
	async def _quit(self, message):
		user = Users.get(self.id)
		if user and (user.in_game or user.in_tournament):
			await Users.disconnect(self.id)
		elif self.manager:
			self.manager.rmv_from_queue(self.id)
		await self.close()

	async def receive(self, text_data):
		await self.update_activity(self.user)
		data = json.loads(text_data)
		message_type = data.get('type')
		action = self._actions.get(message_type)
		if action:
			await action(data)
