from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from .models import Notifications
from django.contrib.auth import get_user_model
import logging
User = get_user_model()

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']  # Assuming you're using Django's custom authentication system
        logger = logging.getLogger('django')
        
        if not self.user.is_authenticated:
            logger.info(f"Connection rejected for user: {self.user}")
            await self.close()
        else:
            logger.info(f"User {self.user} authenticated. Adding to group user_{self.user.id}")
            self.group_name = f'user_{self.user.id}'  # Unique group for each user
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        # Not receiving anything from the WebSocket client for now
        pass

    async def order_notification(self, event):
        message = event['message']
        url = event.get('url', '')  # URL if provided
        
        # Save the notification in the database
        await self.save_notification(message, url)
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'url': url
        }))
    
    @sync_to_async
    def save_notification(self, message, url):
        try:
            Notifications.objects.create(user=self.user, message=message, url=url)
        except Exception as e:
            # Log the error (or handle it in another way)
            print(f"Error saving notification: {e}")
