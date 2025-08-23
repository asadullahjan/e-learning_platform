from django.urls import re_path
from elearning.consumers import ChatConsumer
from elearning.consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<chat_room_id>\w+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
]
