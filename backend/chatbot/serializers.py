from rest_framework import serializers
from .models import Conversation, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_type_display = serializers.CharField(
        source='get_sender_type_display', 
        read_only=True
    )
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender_type', 'sender_type_display', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class ChatQuerySerializer(serializers.Serializer):
    message = serializers.CharField(
        max_length=1000,
        error_messages={
            'required': '메시지를 입력해주세요.',
            'blank': '메시지를 입력해주세요.',
            'max_length': '메시지는 1000자 이내로 입력해주세요.'
        }
    )

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("메시지 내용을 입력해주세요.")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    # messages 필드를 중첩된 관계로 추가
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at', 'messages']

    def validate_title(self, value):
        """제목 유효성 검사"""
        if len(value) < 2:
            raise serializers.ValidationError("제목은 2자 이상 입력해주세요.")
        return value