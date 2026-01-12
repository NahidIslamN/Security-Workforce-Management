from django.urls import path
from .views import *

urlpatterns = [
    path('chat-list/', Chat_Create_lists.as_view(), name="chat-create-list"),    
    path('spam-chat-list/', SpamChatList.as_view(), name='spam-chat-list'), 
    path("accept-private-chat/<int:pk>/", Accept_Leave_Add_People_Chat.as_view(),name='accept-leave-add-chat'),  
    path('message-list/<int:pk>/', MessageList_Chats.as_view(), name='message-list-chat'),
    path('notifications/', Notifications.as_view(), name='notifications'),
    path('unseen-notifications-count/', Unseen_Notifications_count.as_view(), name='unseen-notifications-count'),
    # path('test-message-file/', ChatMessageSocket.as_view(), ),

    path("sent-message/<int:pk>/", Sent_Message_Chats.as_view(), name="send-message"),


]
