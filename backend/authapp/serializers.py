# authapp/serializers.py
from rest_framework import serializers
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
import logging
import uuid

# 로거 설정
logger = logging.getLogger(__name__)

class RegisterSerializer(serializers.Serializer):
    user_login_id = serializers.CharField(
        max_length=100,
        min_length=3,
        error_messages={
            'required': '사용자 ID를 입력해주세요.',
            'blank': '사용자 ID를 입력해주세요.',
            'min_length': '사용자 ID는 최소 3자 이상이어야 합니다.'
        }
    )
    passwd = serializers.CharField(
        max_length=500,
        min_length=8,
        error_messages={
            'required': '비밀번호를 입력해주세요.',
            'blank': '비밀번호를 입력해주세요.',
            'min_length': '비밀번호는 최소 8자 이상이어야 합니다.'
        }
    )
    confirm_pass = serializers.CharField(
        max_length=500,
        error_messages={
            'required': '비밀번호 확인을 입력해주세요.',
            'blank': '비밀번호 확인을 입력해주세요.'
        }
    )
    name = serializers.CharField(
        max_length=50,
        error_messages={
            'required': '이름을 입력해주세요.',
            'blank': '이름을 입력해주세요.'
        }
    )
    dept = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True
    )
    rank = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True
    )
    email = serializers.EmailField(
        max_length=100,
        error_messages={
            'required': '이메일을 입력해주세요.',
            'blank': '이메일을 입력해주세요.',
            'invalid': '올바른 이메일 형식을 입력해주세요.'
        }
    )

    def validate(self, attrs):
        # 비밀번호 일치 확인
        password = attrs.get('passwd')
        confirm_password = attrs.get('confirm_pass')
        
        if password != confirm_password:
            raise serializers.ValidationError({
                'confirm_pass': '비밀번호와 비밀번호 확인이 일치하지 않습니다.'
            })
        
        # 중복 검증
        user_login_id = attrs.get('user_login_id')
        email = attrs.get('email')
        
        try:
            with connection.cursor() as cursor:
                # user_login_id 중복 확인
                cursor.execute("""
                    SELECT user_login_id FROM user_info 
                    WHERE user_login_id = %s
                """, [user_login_id])
                
                if cursor.fetchone():
                    raise serializers.ValidationError({
                        'user_login_id': '이미 사용 중인 사용자 ID입니다.'
                    })
                
                # email 중복 확인
                cursor.execute("""
                    SELECT email FROM user_info 
                    WHERE email = %s
                """, [email])
                
                if cursor.fetchone():
                    raise serializers.ValidationError({
                        'email': '이미 사용 중인 이메일입니다.'
                    })
                    
        except Exception as e:
            logger.error(f"중복 검증 중 오류: {e}")
            raise serializers.ValidationError('사용자 정보 검증 중 오류가 발생했습니다.')
        
        return attrs

    def create(self, validated_data):
        """회원가입 처리"""
        try:
            with connection.cursor() as cursor:
                # 비밀번호 해시화
                hashed_password = make_password(validated_data['passwd'])
                
                # UUID 생성
                user_id = uuid.uuid4()
                
                # 사용자 정보 삽입
                cursor.execute("""
                    INSERT INTO user_info (
                        user_id, user_login_id, passwd, name, dept, rank, email, 
                        created_dt, auth, use_yn
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, 
                        CURRENT_TIMESTAMP, 'N', 'Y'
                    )
                """, [
                    user_id,
                    validated_data['user_login_id'],
                    hashed_password,
                    validated_data['name'],
                    validated_data.get('dept', ''),
                    validated_data.get('rank', ''),
                    validated_data['email']
                ])
                
                # 생성된 사용자 정보 조회
                cursor.execute("""
                    SELECT * FROM user_info WHERE user_id = %s
                """, [user_id])
                
                user_data = cursor.fetchone()
                
                # CustomUser 객체 생성
                class CustomUser:
                    def __init__(self, user_data):
                        self.id = user_data[0]           # user_id
                        self.username = user_data[1]     # user_login_id
                        self.email = user_data[6]        # email
                        self.first_name = user_data[3]   # name
                        self.dept = user_data[4]         # dept
                        self.rank = user_data[5]         # rank
                        self.user_id = user_data[0]      # user_id
                        self.created_dt = user_data[7]   # created_dt
                        self.auth = user_data[8]         # auth
                        self.is_active = user_data[9] == 'Y'  # use_yn
                        self.is_authenticated = True
                        self.is_anonymous = False
                
                custom_user = CustomUser(user_data)
                
                return {
                    'user_id': str(user_id),
                    'user_login_id': validated_data['user_login_id'],
                    'created_dt': user_data[7],
                    'user': custom_user
                }
                
        except Exception as e:
            logger.error(f"회원가입 중 오류: {e}")
            raise ValidationError('회원가입 중 오류가 발생했습니다.')

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
        user_login_id = attrs.get('user_login_id')
        password = attrs.get('passwd')

        if user_login_id and password:
            try:
                with connection.cursor() as cursor:
                    # user_login_id로 사용자 조회 (비밀번호는 WHERE 절에서 제외)
                    cursor.execute("""
                        SELECT * FROM user_info 
                        WHERE user_login_id = %s
                    """, [user_login_id])
                    
                    user_data = cursor.fetchone()
                    
                    if not user_data:
                        # 보안을 위해 구체적인 오류 메시지 제공하지 않음
                        raise serializers.ValidationError('아이디 또는 비밀번호가 올바르지 않습니다.')
                    
                    # use_yn 확인 (활성화된 계정만 로그인 허용)
                    if user_data[9] != 'Y':  # use_yn 컬럼
                        raise serializers.ValidationError('아이디 또는 비밀번호가 올바르지 않습니다.')
                    
                    # 해시된 비밀번호 검증
                    stored_password = user_data[2]  # passwd 컬럼
                    if not check_password(password, stored_password):
                        raise serializers.ValidationError('아이디 또는 비밀번호가 올바르지 않습니다.')
                    
                    # CustomUser 객체 생성
                    class CustomUser:
                        def __init__(self, user_data):
                            self.id = user_data[0]           # user_id
                            self.username = user_data[1]     # user_login_id
                            self.email = user_data[6]        # email
                            self.first_name = user_data[3]   # name
                            self.dept = user_data[4]         # dept
                            self.rank = user_data[5]         # rank
                            self.user_id = user_data[0]      # user_id
                            self.created_dt = user_data[7]   # created_dt
                            self.auth = user_data[8]         # auth
                            self.is_active = user_data[9] == 'Y'  # use_yn
                            self.is_authenticated = True
                            self.is_anonymous = False
                    
                    attrs['user'] = CustomUser(user_data)
                    
            except serializers.ValidationError:
                # ValidationError는 그대로 재발생
                raise
            except Exception as e:
                logger.error(f"사용자 인증 중 오류 발생: {str(e)}")
                raise serializers.ValidationError('아이디 또는 비밀번호가 올바르지 않습니다.')
                
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
        max_length=500,
        min_length=8,  # 최소 8자 이상
        error_messages={
            'required': '새로운 비밀번호를 입력해주세요.',
            'blank': '새로운 비밀번호를 입력해주세요.',
            'min_length': '새 비밀번호는 최소 8자 이상이어야 합니다.'
        }
    )
    confirm_password = serializers.CharField(
        max_length=500,
        error_messages={
            'required': '새 비밀번호 확인을 입력해주세요.',
            'blank': '새 비밀번호 확인을 입력해주세요.'
        }
    )

    def validate(self, attrs):
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        # 새 비밀번호와 확인 비밀번호 일치 검증
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': '새 비밀번호와 확인 비밀번호가 일치하지 않습니다.'
            })
        
        # 현재 비밀번호와 새 비밀번호가 같은지 확인
        if current_password == new_password:
            raise serializers.ValidationError({
                'new_password': '새 비밀번호는 현재 비밀번호와 달라야 합니다.'
            })
        
        return attrs