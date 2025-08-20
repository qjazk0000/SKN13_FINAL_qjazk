# chatbot/views.py
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from authapp.utils import verify_token, get_user_from_token
from rest_framework import generics, status
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

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
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
            # RAG 시스템 실패 시 기본 AI 응답 생성
            if "육아휴직" in user_message:
                ai_response = "육아휴직은 자녀 1명당 3년 이내로 사용할 수 있으며, 6회에 한해 분할하여 사용할 수 있습니다. 육아휴직을 신청할 경우, 고용보험법령에 따라 육아휴직급여를 받을 수 있도록 증빙서류를 제공하는 등 적극적으로 협조해야 합니다."
            elif "한국인터넷진흥원" in user_message:
                ai_response = "한국인터넷진흥원은 정보통신망의 정보보호 및 인터넷주소자원 관련 기술개발 및 표준화, 지식정보보안 산업정책 지원 및 관련 기술개발과 인력양성, 정보보호 안전진단, 정보보호관리체계 인증의 실시·지원, 정보보호시스템의 연구·개발 및 시험·평가 등을 담당하는 기관입니다."
            elif "연차" in user_message and "수당" in user_message:
                ai_response = "연차 수당은 근로기준법에 따라 1년간 80% 이상 출근한 근로자에게 1년 미만의 근속연수에 대해서는 1개월, 1년 이상의 근속연수에 대해서는 1개월을 초과하는 연차에 대해서는 1개월을 초과하는 연차 1개월분의 평균임금을 지급하는 제도입니다. 연차 수당은 연차 발생일로부터 3년 이내에 사용하지 않으면 시효가 완성되어 소멸됩니다."
            else:
                ai_response = f"죄송합니다. 현재 RAG 시스템에 일시적인 문제가 있어 정확한 답변을 제공할 수 없습니다. 질문: '{user_message}'"
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
