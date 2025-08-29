import logging
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from authapp.utils import verify_token
from django.db import connection

logger = logging.getLogger(__name__)

def extract_token_from_header(request):
    """
    요청 헤더에서 JWT 토큰을 추출
    """
    logger.info("=== extract_token_from_header 함수 시작 ===")
    
    # request 객체 정보
    logger.info(f"extract_token_from_header - request 타입: {type(request)}")
    logger.info(f"extract_token_from_header - request.headers 타입: {type(request.headers)}")
    
    # 방법 1: request.headers.get('Authorization')
    auth_header = request.headers.get('Authorization')
    logger.info(f"방법 1 - request.headers.get('Authorization'): {auth_header}")
    
    # 방법 2: request.headers.get('authorization') (소문자)
    auth_header_lower = request.headers.get('authorization')
    logger.info(f"방법 2 - request.headers.get('authorization'): {auth_header_lower}")
    
    # 방법 3: request.META.get('HTTP_AUTHORIZATION')
    http_auth = request.META.get('HTTP_AUTHORIZATION')
    logger.info(f"방법 3 - request.META.get('HTTP_AUTHORIZATION'): {http_auth}")
    
    # 방법 4: request.META에서 'HTTP_' 접두사가 붙은 모든 키 확인
    auth_keys = [k for k in request.META.keys() if k.startswith('HTTP_') and 'AUTH' in k.upper()]
    logger.info(f"방법 4 - HTTP_ 접두사가 붙은 인증 관련 키들: {auth_keys}")
    
    # 방법 5: request.META 전체 키 확인 (디버깅용)
    all_meta_keys = list(request.META.keys())
    logger.info(f"방법 5 - request.META 전체 키들 (처음 20개): {all_meta_keys[:20]}")
    
    # 실제 사용할 헤더 결정
    token_header = auth_header or auth_header_lower or http_auth
    
    if not token_header:
        logger.warning("모든 방법으로 토큰 헤더를 찾을 수 없음")
        logger.info("=== extract_token_from_header 함수 종료 (토큰 없음) ===")
        return None
    
    logger.info(f"사용할 토큰 헤더: {token_header}")
    
    # Bearer 토큰 파싱
    try:
        if token_header.startswith('Bearer '):
            token = token_header.split(' ')[1]
            logger.info(f"토큰 추출 성공: {token[:20]}...")
            logger.info("=== extract_token_from_header 함수 종료 (토큰 추출 성공) ===")
            return token
        else:
            logger.warning(f"Bearer 접두사가 없음: {token_header}")
            logger.info("=== extract_token_from_header 함수 종료 (Bearer 접두사 없음) ===")
            return None
    except Exception as e:
        logger.error(f"토큰 파싱 중 오류: {e}")
        logger.info("=== extract_token_from_header 함수 종료 (파싱 오류) ===")
        return None

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        logger.info("=== admin_required 데코레이터 시작 ===")
        logger.info(f"요청 메서드: {request.method}")
        logger.info(f"요청 경로: {request.path}")
        logger.info(f"요청 URL: {request.build_absolute_uri()}")
        
        # request 객체 정보
        logger.info(f"request 타입: {type(request)}")
        logger.info(f"request.__dict__ 키들: {list(request.__dict__.keys())}")
        
        # 모든 헤더 출력
        logger.info(f"요청 헤더: {dict(request.headers)}")
        
        # META 정보 확인
        logger.info(f"HTTP_AUTHORIZATION: {request.META.get('HTTP_AUTHORIZATION')}")
        logger.info(f"HTTP_AUTHORIZATION (소문자): {request.META.get('HTTP_AUTHORIZATION', '').lower()}")
        
        # Authorization 헤더 직접 확인
        auth_header = request.headers.get('Authorization')
        logger.info(f"request.headers.get('Authorization'): {auth_header}")
        
        # 대소문자 구분 없이 확인
        auth_header_lower = request.headers.get('authorization')
        logger.info(f"request.headers.get('authorization'): {auth_header_lower}")
        
        # request.META에서 인증 관련 키들 확인
        auth_meta_keys = [k for k in request.META.keys() if 'AUTH' in k.upper()]
        logger.info(f"request.META에서 인증 관련 키들: {auth_meta_keys}")
        
        # 토큰 추출
        logger.info("extract_token_from_header 함수 호출 전")
        token = extract_token_from_header(request)
        logger.info(f"extract_token_from_header 함수 호출 후 결과: {token}")
        logger.info(f"추출된 토큰: {token[:20] if token else 'None'}...")
        
        if not token:
            logger.warning("토큰이 헤더에 없음")
            logger.info("=== admin_required 데코레이터 종료 (토큰 없음) ===")
            return Response({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error': 'MISSING_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 토큰 검증
        try:
            payload = verify_token(token)
            if not payload:
                logger.warning("토큰 검증 실패")
                return Response({
                    'success': False,
                    'message': '유효하지 않은 토큰입니다.',
                    'error': 'INVALID_TOKEN'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            user_id = payload.get('user_id')
            if not user_id:
                logger.warning("토큰에서 user_id 추출 실패")
                return Response({
                    'success': False,
                    'message': '사용자 정보를 찾을 수 없습니다.',
                    'error': 'USER_NOT_FOUND'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 관리자 권한 확인
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT auth FROM user_info 
                    WHERE user_id = %s AND use_yn = 'Y'
                """, [user_id])
                
                user_data = cursor.fetchone()
                if not user_data:
                    logger.warning(f"사용자를 찾을 수 없음: {user_id}")
                    return Response({
                        'success': False,
                        'message': '사용자를 찾을 수 없습니다.',
                        'error': 'USER_NOT_FOUND'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                if user_data[0] != 'Y':
                    logger.warning(f"관리자 권한 없음: {user_id}")
                    return Response({
                        'success': False,
                        'message': '관리자 권한이 필요합니다.',
                        'error': 'ADMIN_REQUIRED'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                logger.info(f"관리자 권한 확인 성공: {user_id}")
                
        except Exception as e:
            logger.error(f"토큰 검증 중 오류: {e}")
            return Response({
                'success': False,
                'message': '토큰 검증 중 오류가 발생했습니다.',
                'error': 'TOKEN_VERIFICATION_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info("=== admin_required 데코레이터 종료 (권한 확인 성공) ===")
        return view_func(self, request, *args, **kwargs)
    
    return wrapper