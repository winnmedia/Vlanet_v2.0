from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from users.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    # async def connect(self):
    #     self.username = await self.get_name()
    #     # await database_sync_to_async(self.get_name)()

    # @database_sync_to_async
    # def get_name(self):
    #     user = User.objects.get(id=self.user_id)
    #     if user.nickname:
    #         return user.nickname
    #     else:
    #         return user.username

    #    
    async def connect(self):
        # self.scope['url_route'] = /ws/localhost:8000/ws/chat/1
        self.feedback = self.scope["url_route"]["kwargs"]["feedback_id"]

        #     -> 
        self.feedback_group_name = "chat_%s" % self.feedback

        # Join room group -> group     
        # ->     
        await self.channel_layer.group_add(self.feedback_group_name, self.channel_name)

        await self.accept()

    #     
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.feedback_group_name, self.channel_name
        )

    #    
    async def receive(self, text_data):
        # receive react to django
        text_data_json = json.loads(text_data)
        # message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.feedback_group_name,
            {"type": "chat_message", "message": text_data_json},
        )

    #    
    async def chat_message(self, event):
        # event => {"type": "chat_message", "message": text_data}
        message = event["message"]
        # Send message to WebSocket django to react
        await self.send(text_data=json.dumps({"result": message}))
