from rest_framework import serializers
from .models import Conversation, ChatMessage, ChatReport
from authapp.models import UserInfo

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

class ChatReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatReport
        fields = [
            'report_id',
            'chat',
            'error_type',
            'reason',
            'reported_by',
            'created_at',
            'solved_yn',
            'remark'
        ]
        read_only_fields = [
            'report_id',
            'reported_by',
            'created_at',
            'solved_yn',
            'remark',
            'chat'
        ]

    def create(self, validated_data):
    # UserInfo 기반 reported_by 설정
        user_uuid = getattr(self.context['request'].user, 'user_id', None)
        if not user_uuid:
            raise serializers.ValidationError("사용자 정보 없음")

        user_info = UserInfo.objects.get(user_id=user_uuid)
        validated_data['reported_by'] = user_info

        # chat 확인
        chat = validated_data.get('chat')
        if chat:
            print("✅ chat.id:", chat.id)

        # ChatReport 저장
        chat_report = super().create(validated_data)

        # ChatMessage.report = 'Y' 업데이트
        if chat:
            chat.report = "Y"
            chat.save(update_fields=['report'])

        return chat_report


