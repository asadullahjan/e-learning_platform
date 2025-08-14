from django.urls import re_path
from elearning.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<chat_room_id>\w+)/$", ChatConsumer.as_asgi()),
]
