# authapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.hashers import check_password
from .serializers import (
    LoginSerializer,
    RefreshTokenSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer
)

class LoginView(APIView):
    def post(self, request):  # POST 요청 처리 메소드
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():  # 유효성 검사 통과 시 사용자 정보 추출
            user = serializer.validated_data['user']

            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({  # 성공 응답 반환
                'success': True,
                'message': '로그인 성공',
                'data': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'username': user.username,
                        'email': user.email
                    }
                }
            }, status=status.HTTP_200_OK)
        
        return Response({  # 유효성 검사 실패 시 에러 응답 반환환
            'success': False,
            'message': '회원 정보가 올바르지 않습니다.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):  # GET 요청 처리 메소드
        # 로그인 상태 확인 - GET 요청은 허용하지 않음
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
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)

                return Response({
                    'success': True,
                    'message': '토큰 갱신 성공',
                    'data': {
                        'access_token': new_access_token
                    }
                }, status=status.HTTP_200_OK)
            
            except InvalidToken:
                return Response({
                    'success': False,
                    'message': '유효하지 않은 리프레시 토큰입니다.',
                    'errors': {'refresh': ['토큰이 만료되었거나 유효하지 않습니다.']}
                }, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'success': False,
            'mesage': '입력 데이터가 올바르지 않습니다.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # JWT 토큰 블랙리스트 처리 (선택사항) 이게 뭐야???
            # 현재는 단순히 성공 응답만 반환
            return Response({
                'success': True,
                'message': '로그아웃 성공'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': '로그아웃 처리 중 오류가 발생했습니다.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능하도록 설정 (JWT 토큰 검증)
                                            # 비로그인 사용자(AnonymousUser)는 401 Unauthorized 응답 반환환

    def get(self, request):  # 프로필 조회 메소드
        # 현재 로그인 사용자 정보 반환
        serializer = UserProfileSerializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request):  # 프로필 업데이트 메소드
        # 현재 로그인 사용자 정보 업데이트
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': '프로필이 업데이트 되었습니다.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': '입력 데이터가 올바르지 않습니다.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]  # JWT 토큰 검증

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            try:
                user = request.user
                new_password = serializer.validated_data['new_password']

                # 비밀번호 변경
                user.set_password(new_password)
                user.save()

                return Response({
                    'success': True,
                    'message': '비밀번호가 성공적으로 변경되었습니다.'
                }, status=status.HTTP_200_OK)

            except Exception as e:
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
