# authapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.db import connection
from .serializers import (
    LoginSerializer,
    RefreshTokenSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer
)
from .utils import create_access_token, create_refresh_token, verify_token, get_user_from_token
from .decorators import require_auth
import logging

logger = logging.getLogger(__name__)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # 독립적인 JWT 토큰 생성
            access_token = create_access_token(user)
            refresh_token = create_refresh_token(user)
            
            return Response({
                'success': True,
                'message': '로그인 성공',
                'data': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'user_id': user.user_id,           # UUID
                        'username': user.username,          # user_login_id
                        'email': user.email,                # email
                        'name': user.first_name,            # name
                        'dept': user.dept,                  # dept
                        'rank': user.rank,                  # rank
                        'auth': user.auth,                  # auth - 관리자 권한 확인용
                    }
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': '회원 정보가 올바르지 않습니다.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({
            'success': False,
            'message': 'GET 요청은 지원하지 않습니다. POST 요청을 사용해주세요.',
            'method': 'GET',
            'allowed_methods': ['POST']
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class RefreshTokenView(APIView):
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh']
                
                # 토큰 검증
                payload = verify_token(refresh_token)
                if not payload or payload.get('token_type') != 'refresh':
                    return Response({
                        'success': False,
                        'message': '유효하지 않은 리프레시 토큰입니다.',
                        'error': 'INVALID_REFRESH_TOKEN'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # 사용자 정보 조회
                user_data = get_user_from_token(refresh_token)
                if not user_data:
                    return Response({
                        'success': False,
                        'message': '토큰에 해당하는 사용자를 찾을 수 없습니다.',
                        'error': 'USER_NOT_FOUND'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # 튜플을 CustomUser 객체로 변환
                class CustomUser:
                    def __init__(self, user_data):
                        self.user_id = user_data[0]           # user_id (1번째)
                        self.username = user_data[1]          # user_login_id (2번째)
                        self.email = user_data[6]             # email (7번째)
                        self.first_name = user_data[3]        # name (4번째)
                        self.dept = user_data[4]              # dept (5번째)
                        self.rank = user_data[5]              # rank (6번째)
                        self.created_dt = user_data[7]        # created_dt (8번째)
                
                custom_user = CustomUser(user_data)
                
                # 새로운 액세스 토큰 생성
                new_access_token = create_access_token(custom_user)
                
                return Response({
                    'success': True,
                    'message': '토큰 갱신 성공',
                    'data': {
                        'access_token': new_access_token
                    }
                }, status=status.HTTP_200_OK)
            
            except Exception as e:
                logger.error(f"토큰 갱신 중 오류: {e}")
                return Response({
                    'success': False,
                    'message': '토큰 갱신 중 오류가 발생했습니다.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'success': False,
            'message': '입력 데이터가 올바르지 않습니다.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        try:
            # Authorization 헤더 확인
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response({
                    'success': False,
                    'message': '인증 토큰이 필요합니다.',
                    'error': 'MISSING_TOKEN'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 토큰 추출 및 검증
            from .utils import extract_token_from_header, get_user_from_token
            token = extract_token_from_header(request)
            if not token:
                return Response({
                    'success': False,
                    'message': '인증 토큰이 필요합니다.',
                    'error': 'MISSING_TOKEN'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 토큰 검증
            user_data = get_user_from_token(token)
            if not user_data:
                return Response({
                    'success': False,
                    'message': '토큰이 만료되었거나 유효하지 않습니다.',
                    'error': 'INVALID_TOKEN'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 토큰 블랙리스트 처리는 필요시 구현
            # 현재는 단순히 성공 응답만 반환
            return Response({
                'success': True,
                'message': '로그아웃 성공',
                'redirect_url': '/'  # 프론트엔드에서 사용할 리다이렉트 URL
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"로그아웃 처리 중 오류: {e}")
            return Response({
                'success': False,
                'message': '로그아웃 처리 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(APIView):
    def get(self, request):
        try:
            logger.info(f"UserProfileView GET 요청 시작")
            logger.info(f"요청 메서드: {request.method}")
            logger.info(f"요청 경로: {request.path}")
            
            # Authorization 헤더 확인
            auth_header = request.headers.get('Authorization')
            logger.info(f"Authorization 헤더: {auth_header}")
            
            if not auth_header:
                return Response({
                    'success': False,
                    'message': '인증 토큰이 필요합니다.',
                    'error': 'MISSING_TOKEN'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 토큰 추출
            try:
                token_type, token = auth_header.split(' ')
                if token_type.lower() != 'bearer':
                    return Response({
                        'success': False,
                        'message': '잘못된 토큰 형식입니다.',
                        'error': 'INVALID_TOKEN_FORMAT'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            except ValueError:
                return Response({
                    'success': False,
                    'message': '잘못된 토큰 형식입니다.',
                    'error': 'INVALID_TOKEN_FORMAT'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            logger.info(f"토큰 추출됨: {token[:20]}...")
            
            # 토큰 검증 및 사용자 정보 조회
            from .utils import get_user_from_token
            user_data = get_user_from_token(token)
            
            if not user_data:
                return Response({
                    'success': False,
                    'message': '토큰이 만료되었거나 유효하지 않습니다.',
                    'error': 'INVALID_TOKEN'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            logger.info(f"사용자 데이터 조회 성공: {user_data}")
            
            # 배열 인덱스 범위 확인
            if len(user_data) < 8:
                logger.error(f"user_data 배열 길이 부족: {len(user_data)}")
                return Response({
                    'success': False,
                    'message': '사용자 데이터 형식이 올바르지 않습니다.',
                    'error': 'INVALID_USER_DATA_FORMAT'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'success': True,
                'data': {
                    'user_id': user_data[0],           # UUID (배열 인덱스 유지)
                    'username': user_data[1],          # user_login_id
                    'email': user_data[6],             # email
                    'name': user_data[3],              # name
                    'dept': user_data[4],              # dept
                    'rank': user_data[5],              # rank
                    'created_dt': user_data[7],        # created_dt
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"UserProfileView 에러: {e}")
            import traceback
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            return Response({
                'success': False,
                'message': '프로필 조회 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        # Authorization 헤더 확인
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error': 'MISSING_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 토큰 추출 및 검증
        from .utils import extract_token_from_header, get_user_from_token
        token = extract_token_from_header(request)
        if not token:
            return Response({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error': 'MISSING_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 토큰 검증
        user_data = get_user_from_token(token)
        if not user_data:
            return Response({
                'success': False,
                'message': '토큰이 만료되었거나 유효하지 않습니다.',
                'error': 'INVALID_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 프로필 업데이트 로직 (필요시 구현)
        return Response({
            'success': True,
            'message': '프로필 업데이트 기능은 아직 구현되지 않았습니다.'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

class PasswordChangeView(APIView):
    def post(self, request):
        # Authorization 헤더 확인
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error': 'MISSING_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 토큰 추출 및 검증
        from .utils import extract_token_from_header, get_user_from_token
        token = extract_token_from_header(request)
        if not token:
            return Response({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error': 'MISSING_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 토큰 검증
        user_data = get_user_from_token(token)
        if not user_data:
            return Response({
                'success': False,
                'message': '토큰이 만료되었거나 유효하지 않습니다.',
                'error': 'INVALID_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            try:
                # 현재 비밀번호 확인
                current_password = serializer.validated_data['current_password']
                new_password = serializer.validated_data['new_password']
                
                # user_info 테이블에서 비밀번호 변경
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE user_info 
                        SET passwd = %s 
                        WHERE user_id = %s
                    """, [new_password, user_data[0]])  # user_data[0]은 user_id
                    
                    if cursor.rowcount == 0:
                        return Response({
                            'success': False,
                            'message': '사용자를 찾을 수 없습니다.'
                        }, status=status.HTTP_404_NOT_FOUND)

                return Response({
                    'success': True,
                    'message': '비밀번호가 성공적으로 변경되었습니다.'
                }, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"비밀번호 변경 중 오류: {e}")
                return Response({
                    'success': False,
                    'message': '비밀번호 변경 중 오류가 발생했습니다.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'success': False,
            'message': '입력 데이터가 올바르지 않습니다.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



