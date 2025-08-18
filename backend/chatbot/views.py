# chatbot/views.py
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from .models import Conversation, ChatMessage
from .serializers import ConversationSerializer, ChatMessageSerializer, ChatQuerySerializer

class ConversationListView(generics.ListAPIView):
    """
    대화방 목록 조회
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')

class ConversationCreateView(generics.CreateAPIView):
    """
    새 대화방 생성
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChatQueryView(generics.CreateAPIView):
    """
    질문 전송 및 응답 생성
    """
    serializer_class = ChatQuerySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        session_id = kwargs.get('session_id')
        try:
            conversation = Conversation.objects.get(id=session_id, user=request.user)
        except Conversation.DoesNotExist:
            return Response(
                {"error": "대화방을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 사용자 메시지 저장
        user_message = ChatMessage.objects.create(
            conversation=conversation,
            sender_type='user',
            content=serializer.validated_data['message']
        )
        
        # TODO: AI 응답 생성 로직 구현 (LLM 통합)
        ai_response = "이것은 샘플 AI 응답입니다. 실제로는 AI 모델과 통합해야 합니다."
        
        # AI 응답 저장
        ai_message = ChatMessage.objects.create(
            conversation=conversation,
            sender_type='ai',
            content=ai_response
        )
        
        # 대화방 업데이트 시간 갱신
        conversation.save()
        
        return Response({
            "response": ai_response,
            "message_id": str(ai_message.id)
        }, status=status.HTTP_200_OK)

class ChatStatusView(generics.RetrieveAPIView):
    """
    응답 처리 상태 확인
    """
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        session_id = kwargs.get('session_id')
        try:
            conversation = Conversation.objects.get(id=session_id, user=request.user)
            last_message = conversation.messages.last()
            return Response({
                "status": "completed",
                "last_message": last_message.content if last_message else None,
                "last_updated": conversation.updated_at
            })
        except Conversation.DoesNotExist:
            return Response(
                {"error": "대화방을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
