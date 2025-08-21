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
        # JWT 토큰에서 user_id 추출하여 필터링
        auth_header = self.request.headers.get('Authorization')
        user_id = None
        
        if auth_header:
            try:
                token_type, token = auth_header.split(' ')
                if token_type.lower() == 'bearer':
                    payload = verify_token(token)
                    if payload:
                        user_id = payload.get('user_id')
                        print(f"DEBUG: ConversationListView - JWT에서 추출한 user_id: {user_id}")
            except Exception as e:
                print(f"DEBUG: ConversationListView - JWT 파싱 실패: {str(e)}")
        
        if user_id:
            # user_id로 필터링된 대화방만 반환
            queryset = Conversation.objects.filter(user_id=user_id).order_by('-updated_at')
            print(f"DEBUG: ConversationListView - user_id {user_id}로 필터링된 대화방 수: {queryset.count()}")
            return queryset
        else:
            # user_id가 없으면 빈 쿼리셋 반환
            print(f"DEBUG: ConversationListView - user_id가 없어 빈 결과 반환")
            return Conversation.objects.none()

class ConversationCreateView(generics.CreateAPIView):

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

class ConversationDeleteView(generics.DestroyAPIView):
    """
    개별 채팅 삭제 API
    - JWT 토큰 기반 사용자 인증
    - 본인의 대화기록만 삭제 가능
    - 연관된 채팅 메시지도 함께 삭제
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = ConversationSerializer
    lookup_field = 'conversation_id'
    
    def delete(self, request, *args, **kwargs):
        conversation_id = kwargs.get('conversation_id')
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return Response(
                {'success': False, 'message': '인증 토큰이 필요합니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            # JWT 토큰에서 user_id 추출
            token_type, token = auth_header.split(' ')
            if token_type.lower() != 'bearer':
                return Response(
                    {'success': False, 'message': '올바른 토큰 형식이 아닙니다.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            payload = verify_token(token)
            if not payload:
                return Response(
                    {'success': False, 'message': '유효하지 않은 토큰입니다.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user_id = payload.get('user_id')
            if not user_id:
                return Response(
                    {'success': False, 'message': '사용자 정보를 찾을 수 없습니다.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            print(f"DEBUG: 삭제 요청 - conversation_id: {conversation_id}, user_id: {user_id}")
            
            # 🔒 보안 강화: user_id와 conversation_id를 모두 확인
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id,
                    user_id=user_id  # 반드시 본인의 대화기록만 삭제 가능
                )
                print(f"DEBUG: 권한 확인 성공 - 사용자 {user_id}의 대화기록 {conversation_id}")
            except Conversation.DoesNotExist:
                print(f"DEBUG: 권한 확인 실패 - conversation_id: {conversation_id}, user_id: {user_id}")
                return Response(
                    {'success': False, 'message': '해당 대화기록을 찾을 수 없거나 삭제 권한이 없습니다.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 연관된 채팅 메시지 삭제 (CASCADE 설정이지만 명시적으로 처리)
            chat_messages = ChatMessage.objects.filter(conversation=conversation)
            deleted_message_count = chat_messages.count()
            chat_messages.delete()
            
            # 대화기록 삭제
            conversation_title = conversation.title
            conversation.delete()
            
            print(f"DEBUG: 대화기록 삭제 완료 - ID: {conversation_id}, 제목: {conversation_title}, 삭제된 메시지 수: {deleted_message_count}")
            
            return Response({
                'success': True,
                'message': f'대화기록 "{conversation_title}"이(가) 삭제되었습니다.',
                'data': {
                    'deleted_conversation_id': str(conversation_id),
                    'deleted_message_count': deleted_message_count
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'success': False, 'message': '토큰 형식이 올바르지 않습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"DEBUG: 대화기록 삭제 중 오류 발생: {str(e)}")
            return Response(
                {'success': False, 'message': f'대화기록 삭제 중 오류가 발생했습니다: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            
            # 🔒 보안 강화: user_id와 conversation_id를 모두 확인
            try:
                if user_id:
                    # JWT 토큰이 있는 경우: user_id와 conversation_id 모두 확인
                    conversation = Conversation.objects.get(
                        id=session_id,
                        user_id=user_id  # 반드시 본인의 대화방만 접근 가능
                    )
                    print(f"DEBUG: Conversation 조회 성공 (user_id + conversation_id): {conversation}")
                else:
                    # JWT 토큰이 없는 경우: conversation_id만으로 조회 (개발 단계)
                    conversation = Conversation.objects.get(id=session_id)
                    print(f"DEBUG: Conversation 조회 성공 (conversation_id만): {conversation}")
                    print(f"⚠️ 경고: JWT 토큰이 없어 보안 검증을 건너뜁니다!")
            except Conversation.DoesNotExist:
                print(f"DEBUG: Conversation.DoesNotExist 예외 발생!")
                print(f"DEBUG: 조회하려던 session_id: {session_id}")
                print(f"DEBUG: 조회하려던 user_id: {user_id}")
                return Response({
                    'success': False,
                    'message': '대화방을 찾을 수 없습니다',
                    'errors': {'session_id': '유효하지 않은 세션 ID입니다.'}
                }, status=status.HTTP_404_NOT_FOUND
                )
                
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
        user_message_obj = ChatMessage.objects.create(
            conversation=conversation,
            sender_type='user',
            content=user_message
        )

        # 첫 질문인 경우 대화기록 제목을 질문 내용으로 설정
        if conversation.messages.count() == 1:  # 방금 생성된 사용자 메시지가 첫 번째 메시지
            # 질문 내용을 제목으로 사용 (최대 50자로 제한)
            title = user_message[:50] + "..." if len(user_message) > 50 else user_message
            conversation.title = title
            conversation.save()
            print(f"DEBUG: 첫 질문으로 대화기록 제목 설정: {title}")

        try:
            print(f"DEBUG: RAG 시스템 시작 - 질문: {user_message}")
            # RAG 시스템을 통한 답변 생성
            rag = rag_answer(user_message)
            ai_response = rag["answer"]
            sources = rag["sources"]
            print(f"DEBUG: RAG 시스템 완료 - 응답: {ai_response[:100]}...")
        except Exception as e:
            print(f"DEBUG: RAG 시스템 실패 - 오류: {str(e)}")
            # RAG 시스템 실패 시 기본 AI 응답 생성
            ai_response = f"죄송합니다. RAG 시스템이 실패했습니다. 오류: {str(e)}. 질문: '{user_message}'에 대한 답변을 생성할 수 없습니다."
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
            "conversation_title": conversation.title,  # 업데이트된 제목 반환
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
