import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainApp.settings")
django.setup()

from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
from asgiref.sync import sync_to_async
import json
from .models import PrivateMessage

from channels.db import database_sync_to_async # type: ignore
from django.utils import timezone

from .challenge import Challenge, Data

class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):
  
		self.sender = self.scope["user"]
		if self.sender.is_anonymous:
			await self.close()
			return
		await self.update_activity(self.sender)
		self.receiver_id = self.scope["url_route"]["kwargs"]["receiver_id"]
		self.receiver = await self.get_user(self.receiver_id)

		if self.receiver is None:
			await self.close()
			return
		if self.receiver:
			self.room_name = f"private_{min(self.sender.id, self.receiver.id)}_{max(self.sender.id, self.receiver.id)}"
			self.room_group_name = f"chat_{self.room_name}"
			await self.channel_layer.group_add(self.room_group_name, self.channel_name)
			await self.accept()
			messages = await self.get_previous_messages(self.sender, self.receiver)
			for message in messages:
				sender = await self.get_user(message.sender_id)
				sender_username = sender.username if sender else None
				sender_id = sender.id if sender else None
				await self.send(text_data=json.dumps({
					"message": message.content,
					"sender": sender_username,
					"sender_id": sender_id,
				}))
			if Challenge.get(self.receiver_id):
				await self.send(text_data=json.dumps({"type": 'challenge_received'}))
		else:
			await self.close()

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

	@database_sync_to_async
	def update_activity(self, user):
		profile = user.profile
		profile.is_online = True
		profile.last_activity = timezone.now()
		profile.save(update_fields=['is_online', 'last_activity'])

	async def receive(self, text_data):
		await self.update_activity(self.sender)
		jason = json.loads(text_data)
		if jason.get('type') == 'challenge':
			match jason.get('action'):
				case 'join':
					await Challenge.append(Data(
						self.room_group_name,
						str(self.sender.id),
						self.receiver_id))
				case 'cancel':
					await Challenge.cancel(Data(
						self.room_group_name,
						str(self.sender.id),
						self.receiver_id))
				case 'accept':
					await Challenge.accept(Data(
						self.room_group_name,
						self.receiver_id,
						str(self.sender.id)))
				case 'decline':
					await Challenge.decline(Data(
						self.room_group_name,
						self.receiver_id,
						str(self.sender.id)))
		else:
			message = jason["message"]
			await self.save_message(self.sender, self.receiver, message)
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					"type": "chat_message",
					"message": message,
					"sender": self.sender.id,
					"receiver": self.receiver_id,
				},
			)

	async def joinFight(self, event):
		if event['opponent_id'] == str(self.sender.id):
			await self.send(text_data=json.dumps({
				"type": 'challenge_received',
			}))
	
	async def quitFight(self, event):
		if event['opponent_id'] == str(self.sender.id):
			await self.send(text_data=json.dumps({
				"type": 'challenge_cancelled',
			}))
	
	async def declineFight(self, event):
		if event['challenger_id'] == str(self.sender.id):
			await self.send(text_data=json.dumps({
				"type": 'challenge_declined',
			}))
	async def acceptFight(self, event):
		await self.send(text_data=json.dumps({
			"type": 'challenge_accepted',
			"game_id": event['game_id'],
		}))


	# @database_sync_to_async
	# def checkBlocked(self, sender):
	# 	return (sender.profile.friends.filter(id=self.receiver_id).exists() or self.receiver.profile.friends.filter(id=sender.id).exists())

	async def chat_message(self, event):
		sender = await self.get_user(event["sender"])
		sender_username = sender.username if sender else None
		sender_id = sender.id if sender else None

		# blocked = await self.checkBlocked(sender)
		# if (blocked):
		# 	return
		await self.send(text_data=json.dumps({
			"message": event["message"],
			"sender": sender_username,
			"sender_id": sender_id,
		}))
	
	
	@sync_to_async
	def get_user(self, user_id):
		try:
			return User.objects.get(id=user_id)
		except User.DoesNotExist:
			return None

	def get_user_channel(self, user_id):
		try:
			user = User.objects.get(id=user_id)
			return user.profile.channel_name
		except User.DoesNotExist:
			return None

	@sync_to_async
	def get_previous_messages(self, sender, receiver):
		return list(PrivateMessage.objects.filter(
			sender__in=[sender, receiver],
			receiver__in=[sender, receiver]
		).order_by('timestamp'))

	@sync_to_async
	def save_message(self, sender, receiver, content):
		PrivateMessage.objects.create(sender=sender, receiver=receiver, content=content)

	@sync_to_async
	def get_username(self, sender):
		""" Fetch sender's username in a sync-to-async context. """
		return sender.username if sender else None