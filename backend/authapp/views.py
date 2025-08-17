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
                        'auth': user.auth,                  # auth
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
                
                # 새로운 액세스 토큰 생성
                new_access_token = create_access_token(user_data)
                
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
    @require_auth
    def post(self, request):
        try:
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
    @require_auth
    def get(self, request):
        # request.user_data에는 이미 사용자 정보가 들어있음
        user_data = request.user_data
        
        return Response({
            'success': True,
            'data': {
                'user_id': user_data[0],           # UUID (배열 인덱스 유지)
                'username': user_data[1],          # user_login_id
                'email': user_data[6],             # email
                'name': user_data[3],              # name
                'dept': user_data[4],              # dept
                'rank': user_data[5],              # rank
                'auth': user_data[8],              # auth
                'created_dt': user_data[7],        # created_dt
            }
        }, status=status.HTTP_200_OK)

    @require_auth
    def put(self, request):
        # 프로필 업데이트 로직 (필요시 구현)
        return Response({
            'success': True,
            'message': '프로필 업데이트 기능은 아직 구현되지 않았습니다.'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

class PasswordChangeView(APIView):
    @require_auth
    def post(self, request):
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
                    """, [new_password, request.user_id])
                    
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
