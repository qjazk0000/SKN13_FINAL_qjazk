# chatbot/views.py
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status, viewsets
from .models import Conversation, ChatMessage
from .serializers import ConversationSerializer, ChatMessageSerializer, ChatQuerySerializer

class ConversationViewSet(generics.ListAPIView):
    """
    기존 대화방 목록 조회
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')

class ConversationCreateView(generics.ListAPIView):
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

# @api_view(['GET'])
# def chat_history(request):
#     """채팅 세션 목록 조회"""
#     sessions = ChatSession.objects.all()
#     serializer = ChatSessionSerializer(sessions, many=True)
#     return Response(serializer.data)

# @api_view(['POST'])
# def create_chat(request):
#     """새 채팅 세션 생성"""
#     session_id = f"{int(time.time() * 1000)}"
#     session = ChatSession.objects.create(
#         session_id=session_id,
#         title="새로운 대화"
#     )
#     serializer = ChatSessionSerializer(session)
#     return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(['GET'])
# def get_chat_messages(request, session_id):
#     """특정 채팅 세션의 메시지 조회"""
#     try:
#         session = ChatSession.objects.get(session_id=session_id)
#         messages = session.messages.all()
#         serializer = ChatMessageSerializer(messages, many=True)
#         return Response(serializer.data)
#     except ChatSession.DoesNotExist:
#         return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

# @api_view(['POST'])
# def send_message(request):
#     """메시지 전송 및 AI 응답"""
#     data = request.data
#     session_id = data.get('session_id')
#     message_content = data.get('message')
#     message_type = data.get('type', 'text')
    
#     try:
#         session = ChatSession.objects.get(session_id=session_id)
        
#         # 사용자 메시지 저장
#         user_message = ChatMessage.objects.create(
#             session=session,
#             sender='user',
#             content=message_content,
#             message_type=message_type
#         )
        
#         # AI 응답 생성 (더미)
#         ai_response = f"AI 응답: {message_content}"
#         ai_message = ChatMessage.objects.create(
#             session=session,
#             sender='ai',
#             content=ai_response,
#             message_type='text'
#         )
        
#         # 세션 제목 업데이트 (첫 번째 메시지인 경우)
#         if session.messages.count() == 2:  # 사용자 메시지 + AI 응답
#             session.title = message_content[:50]
#             session.save()
        
#         return Response({
#             'user_message': ChatMessageSerializer(user_message).data,
#             'ai_message': ChatMessageSerializer(ai_message).data
#         })
        
#     except ChatSession.DoesNotExist:
#         return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

# @api_view(['PUT'])
# def update_chat_title(request, session_id):
#     """채팅 세션 제목 업데이트"""
#     try:
#         session = ChatSession.objects.get(session_id=session_id)
#         session.title = request.data.get('title', session.title)
#         session.save()
#         serializer = ChatSessionSerializer(session)
#         return Response(serializer.data)
#     except ChatSession.DoesNotExist:
#         return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

# @api_view(['DELETE'])
# def delete_chat(request, session_id):
#     """채팅 세션 삭제"""
#     try:
#         session = ChatSession.objects.get(session_id=session_id)
#         session.delete()
#         return Response({'message': 'Chat session deleted'})
#     except ChatSession.DoesNotExist:
#         return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
