# authapp/decorators.py
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .utils import extract_token_from_header, get_user_from_token
import logging

logger = logging.getLogger(__name__)

def require_auth(view_func):
    """인증이 필요한 API에 사용하는 데코레이터"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # request 객체가 제대로 전달되었는지 확인
        logger.info(f"request 객체 타입: {type(request)}")
        logger.info(f"request 객체 속성들: {dir(request)}")
        logger.info(f"request 객체 내용: {request}")
        
        if not hasattr(request, 'method'):
            logger.error("request 객체에 method 속성이 없습니다")
            return Response({
                'success': False,
                'message': '잘못된 요청입니다.',
                'error': 'INVALID_REQUEST'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        logger.info(f"인증 요청: {request.method} {request.path}")
        
        # Authorization 헤더 확인
        auth_header = request.headers.get('Authorization')
        logger.info(f"Authorization 헤더: {auth_header}")
        
        # 토큰 추출
        token = extract_token_from_header(request)
        if not token:
            logger.warning("토큰이 헤더에 없음")
            return Response({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error': 'MISSING_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        logger.info(f"토큰 추출됨: {token[:20]}...")
        
        # 토큰 검증 및 사용자 정보 조회
        user_data = get_user_from_token(token)
        if not user_data:
            logger.warning(f"토큰 검증 실패: {token[:20]}...")
            return Response({
                'success': False,
                'message': '토큰이 만료되었거나 유효하지 않습니다.',
                'error': 'INVALID_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # request 객체에 사용자 정보 추가
        request.user_data = user_data
        request.user_id = user_data[0]
        request.username = user_data[1]
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

def require_admin(view_func):
    """관리자 권한이 필요한 API에 사용하는 데코레이터"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # request 객체가 제대로 전달되었는지 확인
        logger.info(f"require_admin - request 객체 타입: {type(request)}")
        logger.info(f"require_admin - request 객체 속성들: {dir(request)}")
        logger.info(f"require_admin - request 객체 내용: {request}")
        
        if not hasattr(request, 'method'):
            logger.error("request 객체에 method 속성이 없습니다")
            return Response({
                'success': False,
                'message': '잘못된 요청입니다.',
                'error': 'INVALID_REQUEST'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # 먼저 인증 확인
        token = extract_token_from_header(request)
        if not token:
            return Response({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error': 'MISSING_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 토큰 검증 및 사용자 정보 조회
        user_data = get_user_from_token(token)
        if not user_data:
            logger.warning(f"토큰 검증 실패: {token[:20]}...")
            return Response({
                'success': False,
                'message': '토큰이 만료되었거나 유효하지 않습니다.',
                'error': 'INVALID_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 관리자 권한 확인 (예: auth 컬럼이 'Y'인 경우)
        if user_data[8] != 'Y':  # auth 컬럼
            return Response({
                'success': False,
                'message': '관리자 권한이 필요합니다.',
                'error': 'INSUFFICIENT_PERMISSIONS'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # request 객체에 사용자 정보 추가
        request.user_data = user_data
        request.user_id = user_data[0]
        request.username = user_data[1]
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
