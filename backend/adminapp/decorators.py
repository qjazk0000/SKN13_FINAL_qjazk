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
        # 토큰 추출
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
            return Response({
                'success': False,
                'message': '유효하지 않은 토큰입니다.',
                'error': 'INVALID_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 관리자 권한 확인 (auth 컬럼이 'Y'인 경우)
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