# chatbot/views.py
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from authapp.utils import verify_token, get_user_from_token
from rest_framework import generics, status, viewsets
from .models import Conversation, ChatMessage
from .serializers import ConversationSerializer, ChatMessageSerializer, ChatQuerySerializer
from .services.rag_service import rag_answer


class ConversationListView(generics.ListAPIView):

    """
    대화방 목록 조회
    """
    authentication_classes = []  # 개발 단계에서는 인증 클래스 제거
    permission_classes = [AllowAny]  # 개발 단계에서는 AllowAny
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')

class ConversationCreateView(generics.ListAPIView):

    """
    새 대화방 생성
    """
    authentication_classes = []  # 개발 단계에서는 인증 클래스 제거
    permission_classes = [AllowAny]  # 개발 단계에서는 AllowAny
    serializer_class = ConversationSerializer

    def perform_create(self, serializer):
        # 디버깅을 위한 로그 추가
        print(f"DEBUG: ConversationCreateView.perform_create() 호출됨")
        print(f"DEBUG: request.data = {self.request.data}")
        print(f"DEBUG: request.user = {getattr(self.request, 'user', 'No user')}")
        
        # JWT 토큰이 있으면 user_id 사용, 없으면 요청 데이터에서 가져오기
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            user_id = self.request.user.id
            print(f"DEBUG: 인증된 사용자에서 user_id = {user_id}")
            serializer.save(user_id=user_id)
        else:
            # 개발 단계에서는 요청 데이터에서 user_id 가져오기
            user_id = self.request.data.get('user_id')
            print(f"DEBUG: 요청 데이터에서 user_id = {user_id}")
            if user_id:
                serializer.save(user_id=user_id)
            else:
                print(f"DEBUG: user_id가 없어 기본값으로 저장")
                serializer.save()
        
        # 저장된 객체 확인
        saved_obj = serializer.instance
        print(f"DEBUG: 저장된 객체 = {saved_obj}")
        print(f"DEBUG: 저장된 객체 ID = {saved_obj.id}")
        print(f"DEBUG: 저장된 객체 user_id = {saved_obj.user_id}")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': '대화방이 생성되었습니다',
            'data': response.data
        }, status=status.HTTP_201_CREATED)

class ChatQueryView(generics.CreateAPIView):
    """
    질문 전송 및 응답 생성
    """
    authentication_classes = []  # 인증 클래스 제외
    permission_classes = [AllowAny]  # 개발 단계에서는 인증 우회
    serializer_class = ChatQuerySerializer

    def create(self, request, *args, **kwargs):
        session_id = kwargs.get('session_id')
        
        # 디버깅을 위한 로그 추가
        print(f"DEBUG: ChatQueryView.create() 호출됨")
        print(f"DEBUG: session_id = {session_id}")
        print(f"DEBUG: kwargs = {kwargs}")
        print(f"DEBUG: request.path = {request.path}")
        
        # JWT 토큰에서 사용자 정보 추출
        auth_header = request.headers.get('Authorization')
        user_id = None
        
        if auth_header:
            try:
                token_type, token = auth_header.split(' ')
                if token_type.lower() == 'bearer':
                    payload = verify_token(token)
                    if payload:
                        user_id = payload.get('user_id')
            except:
                pass
        
        try:
            # 디버깅을 위한 로그 추가
            print(f"DEBUG: Conversation 조회 시도 - session_id: {session_id}")
            print(f"DEBUG: Conversation 조회 시도 - user_id: {user_id}")
            
            # 데이터베이스에 해당 ID가 존재하는지 확인
            all_conversations = Conversation.objects.all()
            print(f"DEBUG: 데이터베이스의 모든 Conversation: {list(all_conversations.values('id', 'user_id', 'title'))}")
            
            # 먼저 ID로만 조회 시도 (user_id 무시)
            try:
                conversation = Conversation.objects.get(id=session_id)
                print(f"DEBUG: Conversation 조회 성공 (ID만으로): {conversation}")
            except Conversation.DoesNotExist:
                print(f"DEBUG: Conversation.DoesNotExist 예외 발생!")
                print(f"DEBUG: 조회하려던 session_id: {session_id}")
                print(f"DEBUG: 조회하려던 user_id: {user_id}")
                return Response({
                    'success': False,
                    'message': '대화방을 찾을 수 없습니다',
                    'errors': {'session_id': '유효하지 않은 세션 ID입니다.'}
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            print(f"DEBUG: 예상치 못한 오류 발생: {str(e)}")
            return Response({
                'success': False,
                'message': '대화방 조회 중 오류가 발생했습니다',
                'errors': {'error': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_message = serializer.validated_data['message']

        # 사용자 메시지 저장
        ChatMessage.objects.create(
            conversation=conversation,
            sender_type='user',
            content=user_message
        )

        try:
            print(f"DEBUG: RAG 시스템 시작 - 질문: {user_message}")
            # RAG 시스템을 통한 답변 생성
            rag = rag_answer(user_message)
            ai_response = rag["answer"]
            sources = rag["sources"]
            print(f"DEBUG: RAG 시스템 완료 - 응답: {ai_response[:100]}...")
        except Exception as e:
            print(f"DEBUG: RAG 시스템 실패 - 오류: {str(e)}")
            sources = []

        # AI 응답 저장
        ai_msg = ChatMessage.objects.create(
            conversation=conversation,
            sender_type='ai',
            content=ai_response
        )
        
        # 대화방 업데이트 시간 갱신
        conversation.save()

        return Response({
            "response": ai_response,
            "message_id": str(ai_msg.id),
            "sources": sources,
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
