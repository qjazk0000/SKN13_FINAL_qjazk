# authapp/serializers.py
from rest_framework import serializers
from django.db import connection
from django.contrib.auth.hashers import check_password
import logging

# 로거 설정
logger = logging.getLogger(__name__)

class LoginSerializer(serializers.Serializer):
    user_login_id = serializers.CharField(
        max_length=150,
        error_messages={
            'required': '사용자 ID를 입력해주세요.',
            'blank': '사용자 ID를 입력해주세요.'
        }
    )
    passwd = serializers.CharField(
        max_length=128,
        error_messages={
            'required': '비밀번호를 입력해주세요',
            'blank': '비밀번호를 입력해주세요'
        }
    )

    def validate(self, attrs):
        # user_info 테이블에서 직접 사용자 인증
        user_login_id = attrs.get('user_login_id')
        password = attrs.get('passwd')

        if user_login_id and password:
            try:
                with connection.cursor() as cursor:
                    # user_info 테이블에서 사용자 조회
                    cursor.execute("""
                        SELECT * FROM user_info 
                        WHERE user_login_id = %s AND passwd = %s
                    """, [user_login_id, password])
                    
                    user_data = cursor.fetchone()
                    
                    if not user_data:
                        raise serializers.ValidationError('아이디 또는 비밀번호가 올바르지 않습니다.')
                    
                    # 디버깅을 위한 로그 출력 (print 대신 logger 사용)
                    logger.info(f"사용자 데이터 조회 성공: {user_data[1]}")  # user_login_id
                    logger.info(f"auth 컬럼 값: {user_data[8]}")  # auth (9번째)
                    logger.info(f"use_yn 컬럼 값: {user_data[9]}")  # use_yn (10번째)
                    
                    # 사용자 상태 확인 (올바른 인덱스 사용)
                    if user_data[9] != 'Y':  # use_yn 컬럼 (10번째)
                        raise serializers.ValidationError('비활성화된 계정입니다.')
                    
                    # auth 컬럼은 관리자 권한을 나타내는 컬럼으로 로그인 가능 여부와는 상관없음
                    # if user_data[8] != 'Y':  # auth 컬럼 (9번째)
                    #     raise serializers.ValidationError('인증되지 않은 계정입니다.')
                    
                    # 사용자 정보를 CustomUser 객체로 변환
                    # CustomUser 클래스는 사용자 정보를 담는 객체로 정의
                    class CustomUser:
                        def __init__(self, user_data):
                            self.id = user_data[0]           # user_id (1번째) - JWT 토큰 생성에 필요
                            
                            self.username = user_data[1]      # user_login_id (2번째)
                            self.email = user_data[6]         # email (7번째)
                            self.first_name = user_data[3]    # name (4번째)
                            self.dept = user_data[4]          # dept (5번째)
                            self.rank = user_data[5]          # rank (6번째)
                            self.user_id = user_data[0]       # user_id (1번째)
                            self.created_dt = user_data[7]    # created_dt (8번째)
                            self.auth = user_data[8]          # auth (9번째) - 관리자 권한 확인용
                            # auth 컬럼은 관리자 권한을 나타내는 컬럼으로 로그인 가능 여부와는 상관없음
                            # self.auth = user_data[8]          # auth (9번째)
                            self.is_active = user_data[9] == 'Y'  # use_yn (10번째)
                            self.is_authenticated = True
                            self.is_anonymous = False
                    
                    attrs['user'] = CustomUser(user_data)
                    
            except Exception as e:
                logger.error(f"사용자 인증 중 오류 발생: {str(e)}")
                raise serializers.ValidationError(f'사용자 인증 중 오류가 발생했습니다: {str(e)}')
                
        return attrs

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        error_messages={
            'required': '리프레시 토큰이 필요합니다.',
            'blank': '리프레시 토큰이 필요합니다.'
        }
    )

class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    dept = serializers.CharField(required=False, allow_blank=True)
    rank = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.CharField(required=False, allow_blank=True)
    created_dt = serializers.DateTimeField(required=False)
    auth = serializers.CharField(required=False, allow_blank=True)  # 관리자 권한 확인용
    # auth 컬럼은 관리자 권한을 나타내는 컬럼으로 로그인 가능 여부와는 상관없음
    # auth = serializers.CharField(required=False, allow_blank=True)
    
    def to_representation(self, instance):
        # CustomUser 객체에서 데이터 추출
        return {
            'username': getattr(instance, 'username', ''),
            'email': getattr(instance, 'email', ''),
            'first_name': getattr(instance, 'first_name', ''),
            'dept': getattr(instance, 'dept', ''),
            'rank': getattr(instance, 'rank', ''),
            'user_id': getattr(instance, 'user_id', ''),
            'created_dt': getattr(instance, 'created_dt', ''),
            'auth': getattr(instance, 'auth', 'N')  # 관리자 권한 확인용
            # auth 컬럼은 관리자 권한을 나타내는 컬럼으로 로그인 가능 여부와는 상관없음
            # 'auth': getattr(instance, 'auth', '')

        }

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        max_length=128,
        error_messages={
            'required': '현재 비밀번호를 입력해주세요.',
            'blank': '현재 비밀번호를 입력해주세요.'
        }
    )
    new_password = serializers.CharField(
        max_length=128,
        min_length=8,  # 최소 8자 이상
        error_messages={
            'required': '새로운 비밀번호를 입력해주세요.',
            'blank': '새로운 비밀번호를 입력해주세요.',
            'min_length': '새 비밀번호는 최소 8자 이상이어야 합니다.'
        }
    )

    def validate(self, attrs):
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')

        # 새 비밀번호가 현재 비밀번호와 다른지 확인
        if current_password == new_password:
            raise serializers.ValidationError({
                'new_password': '새 비밀번호는 현재 비밀번호와 달라야 합니다.'
            })
        
        return attrs