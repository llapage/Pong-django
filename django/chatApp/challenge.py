import uuid

from channels.layers import get_channel_layer # type: ignore
from dataclasses import dataclass

@dataclass
class Data:
	room_group_name: str
	challenger_id: str
	opponent_id: str


class Challenge():

	_queue = {}
	_channel_layer = get_channel_layer()

	@classmethod
	async def send_message(cls, data: Data, consumer_function: str):
		await cls._channel_layer.group_send(
			data.room_group_name,
			{
				"type": consumer_function,
				"challenger_id": data.challenger_id,
				"opponent_id": data.opponent_id,
			})

	@classmethod
	def get(cls, challenger_id: str):
		return cls._queue.get(challenger_id, None)

	@classmethod
	async def append(cls, data: Data):
		if data.challenger_id not in cls._queue:
			cls._queue[data.challenger_id] = data.opponent_id
			await cls.send_message(data, "joinFight")

	@classmethod
	async def cancel(cls, data: Data):
		if data.challenger_id in cls._queue:
			del cls._queue[data.challenger_id]
			await cls.send_message(data, "quitFight")

	
	@classmethod
	async def decline(cls, data: Data):
		if data.challenger_id in cls._queue:
			del cls._queue[data.challenger_id]
			await cls.send_message(data, "declineFight")
	
	@classmethod
	async def accept(cls, data: Data):
		if data.challenger_id in cls._queue:
			del cls._queue[data.challenger_id]
			game_id = uuid.uuid4().hex
			await cls._channel_layer.group_send(
				data.room_group_name,
				{
					"type": "acceptFight",
					"game_id": game_id,
				})