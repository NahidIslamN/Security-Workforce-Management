from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name','last_name', 'image', 'last_activity']


# class ChatListSerializer(serializers.ModelSerializer):
#     participants = serializers.SerializerMethodField()

#     class Meta:
#         model = Chat
#         fields = ['id', 'participants']

#     def get_participants(self, obj):
#         request = self.context.get('request')
#         if not request:
#             return UserSerializer(obj.participants.all(), many=True).data

#         # exclude current user
#         users = obj.participants.exclude(id=request.user.id)
#         return UserSerializer(users, many=True).data

class MessagePreviewSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.first_name')

    class Meta:
        model = Message
        fields = ['id', 'text', 'sender_name', 'created_at']


class ChatListSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = [
            'id',
            'participants',
            'last_message',
            'last_message_time',
            'updated_at'
        ]

    def get_participants(self, obj):
        request = self.context.get('request')
        users = obj.participants.exclude(id=request.user.id)
        return UserSerializer(users, many=True).data

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return MessagePreviewSerializer(last_msg).data
        return None

    def get_last_message_time(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        return last_msg.created_at if last_msg else None



class ChatListSerializerCreate(serializers.ModelSerializer):
    participants = participants = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = [
            'id',
            'participants'
        ]
    def get_participants(self, obj):
        request = self.context.get('request')
        users = obj.participants.exclude(id=request.user.id)
        return UserSerializer(users, many=True).data





class Message_List_Serializer(serializers.ModelSerializer):
    sender = UserSerializer()
    class Meta:
        model = Message
        fields = ['text', "sender"]
       


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=NoteModel
        fields = ["id","title","content","note_type"]
        




class Chat_or_Group_CreateSerializer(serializers.Serializer):
    user_list = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    group_name = serializers.CharField(
        required=False,
        allow_blank=True,
        default=""
    )



class Add_People_Group_CreateSerializer(serializers.Serializer):
    user_list = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    

class Send_Message_Serializer(serializers.Serializer):
    message = serializers.CharField(
        required=False,
        allow_blank=True,
        default=""
    )
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True
    )
  