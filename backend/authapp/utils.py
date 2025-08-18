# authapp/utils.py
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.db import connection
import logging

logger = logging.getLogger(__name__)

# JWT 설정
JWT_SECRET_KEY = getattr(settings, 'SECRET_KEY', 'dev-secret-key')
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME = timedelta(hours=1)      # 1시간
REFRESH_TOKEN_LIFETIME = timedelta(days=7)      # 7일

def create_access_token(user_data):
    """액세스 토큰 생성"""
    payload = {
        'token_type': 'access',
        'user_id': str(user_data.user_id),        # CustomUser 객체의 속성으로 접근
        'username': user_data.username,           # user_login_id
        'email': user_data.email,                 # email
        'name': user_data.first_name,             # name
        'dept': user_data.dept,                   # dept
        'rank': user_data.rank,                   # rank
        # 'auth': user_data.auth,                   # auth
        'iat': datetime.now(timezone.utc),        # 토큰 발급 시간
        'exp': datetime.now(timezone.utc) + ACCESS_TOKEN_LIFETIME,  # 만료 시간
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def create_refresh_token(user_data):
    """리프레시 토큰 생성"""
    payload = {
        'token_type': 'refresh',
        'user_id': str(user_data.user_id),        # CustomUser 객체의 속성으로 접근
        'username': user_data.username,           # user_login_id
        'iat': datetime.now(timezone.utc),        # 토큰 발급 시간
        'exp': datetime.now(timezone.utc) + REFRESH_TOKEN_LIFETIME,  # 만료 시간
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_token(token):
    """토큰 검증 및 디코딩"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("토큰이 만료되었습니다.")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"유효하지 않은 토큰입니다: {e}")
        return None

def get_user_from_token(token):
    """토큰에서 사용자 정보 추출"""
    payload = verify_token(token)
    if not payload:
        logger.warning("토큰 검증 실패 - payload가 None")
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM user_info 
                WHERE user_id = %s
            """, [payload['user_id']])
            
            user_data = cursor.fetchone()
            if not user_data:
                logger.warning(f"사용자 정보를 찾을 수 없음: {payload['user_id']}")
                return None
            
            # 사용자 상태 확인
            if user_data[9] != 'Y':  # use_yn
                logger.warning(f"비활성화된 계정: {payload['username']}")
                return None
            
            # if user_data[8] != 'Y':  # auth
            #     logger.warning(f"인증되지 않은 계정: {payload['username']}")
            #     return None
            
            logger.info(f"사용자 정보 조회 성공: {payload['username']}")
            return user_data
            
    except Exception as e:
        logger.error(f"사용자 정보 조회 중 오류: {e}")
        return None

def extract_token_from_header(request):
    """HTTP 헤더에서 토큰 추출"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        token_type, token = auth_header.split(' ')
        if token_type.lower() != 'bearer':
            return None
        return token
    except ValueError:
        return None
