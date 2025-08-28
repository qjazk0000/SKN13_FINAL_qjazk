# authapp/utils.py
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.db import connection
import logging
import uuid

logger = logging.getLogger(__name__)

# JWT 설정
JWT_SECRET_KEY = getattr(settings, 'SECRET_KEY', 'dev-secret-key')
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME = timedelta(hours=1)      # 1시간
REFRESH_TOKEN_LIFETIME = timedelta(days=7)      # 7일

def create_access_token(user_data):
    """액세스 토큰 생성"""
    payload = {
        'jti': str(uuid.uuid4()),  # 고유 식별자
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
        'jti': str(uuid.uuid4()),  # 고유 식별자
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
    try:
        payload = verify_token(token)
        if not payload or payload.get("token_type") not in ("access", "refresh"):
            return None
        
        logger.info(f"토큰 payload: {payload}")
        user_id = payload.get('user_id')
        logger.info(f"추출된 user_id: {user_id}")
        
        with connection.cursor() as cursor:
            logger.info(f"데이터베이스 쿼리 실행: SELECT * FROM user_info WHERE user_id = {user_id}")
            cursor.execute("""
                SELECT * FROM user_info 
                WHERE user_id = %s
            """, [user_id])
            
            user_data = cursor.fetchone()
            if not user_data:
                logger.warning(f"사용자 정보를 찾을 수 없음: {user_id}")
                return None
            
            logger.info(f"사용자 데이터 조회됨: {user_data}")
            
            # 사용자 상태 확인
            if user_data[9] != 'Y':  # use_yn
                logger.warning(f"비활성화된 계정: {user_data[1] if len(user_data) > 1 else 'unknown'}")
                return None
            
            logger.info(f"사용자 정보 조회 성공: {user_data[1] if len(user_data) > 1 else 'unknown'}")
            return user_data
            
    except Exception as e:
        logger.error(f"사용자 정보 조회 중 오류: {e}")
        logger.error(f"오류 타입: {type(e)}")
        import traceback
        logger.error(f"스택 트레이스: {traceback.format_exc()}")
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
