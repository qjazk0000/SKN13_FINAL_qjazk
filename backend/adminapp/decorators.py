# adminapp/decorators.py
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from authapp.utils import extract_token_from_header, get_user_from_token
import logging

logger = logging.getLogger(__name__)

def admin_required(view_func):
    """관리자 권한이 필요한 API에 사용하는 데코레이터 (adminapp 전용)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        logger.info(f"admin_required 데코레이터 실행: {request.method} {request.path}")
        logger.info(f"요청 헤더: {dict(request.headers)}")
        
        # 토큰 추출
        token = extract_token_from_header(request)
        logger.info(f"추출된 토큰: {token[:20] if token else 'None'}...")
        
        if not token:
            logger.warning("토큰이 헤더에 없음")
            return Response({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error': 'MISSING_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 토큰 검증 및 사용자 정보 조회
        logger.info("토큰 검증 시작")
        user_data = get_user_from_token(token)
        logger.info(f"사용자 데이터 조회 결과: {user_data is not None}")
        
        if not user_data:
            logger.warning("토큰 검증 실패")
            return Response({
                'success': False,
                'message': '유효하지 않은 토큰입니다.',
                'error': 'INVALID_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 관리자 권한 확인 (auth 컬럼이 'Y'인 경우)
        logger.info(f"사용자 auth 값: {user_data[8] if len(user_data) > 8 else 'N/A'}")
        if user_data[8] != 'Y':  # auth 컬럼
            logger.warning(f"관리자 권한 없음: {user_data[8]}")
            return Response({
                'success': False,
                'message': '관리자 권한이 필요합니다.',
                'error': 'INSUFFICIENT_PERMISSIONS'
            }, status=status.HTTP_403_FORBIDDEN)
        
        logger.info("관리자 권한 확인 완료")
        
        # request 객체에 사용자 정보 추가
        request.user_data = user_data
        request.user_id = user_data[0]
        request.username = user_data[1]
        
        return view_func(request, *args, **kwargs)
    
    return wrapper