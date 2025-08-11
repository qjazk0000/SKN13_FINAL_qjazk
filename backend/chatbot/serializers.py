# chatbot/serializers.py
from rest_framework import serializers
from .models import Conversation, ChatMessage

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender_type', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class ChatQuerySerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)