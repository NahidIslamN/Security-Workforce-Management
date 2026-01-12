from django.urls import path
from chat_app import consumers

websocket_urlpatterns = [
    path(r'ws/asc/notifications/', consumers.NotificationConsumer.as_asgi()),
    # path(r'ws/asc/chat/<int:chat_id>/', consumers.ChatConsumer.as_asgi()),
    path(r'ws/asc/update_chat_messages/', consumers.ChatConsumer.as_asgi()),
    # path(r'ws/asc/reaction/<int:message_id>/', consumers.Sent_Reaction_ON_Message.as_asgi()),
    path(r'ws/asc/chat/seen_status_update/<int:chat_id>/', consumers.MessageSeenStatusUpdate.as_asgi()),
    path(r"ws/asc/location_change/", consumers.Location_Change_Websocket.as_asgi()),


    # update chat consumers
    
]
