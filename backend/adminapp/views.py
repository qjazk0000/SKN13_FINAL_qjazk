# adminapp/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from authapp.utils import extract_token_from_header, get_user_from_token
import logging

logger = logging.getLogger(__name__)

class AdminUsersView(APIView):
    """
    관리자용 회원 조회 API
    GET /api/admin/users?filter={field}:{value}
    """
    
    def get(self, request):
        # Authorization 헤더 확인
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error': 'MISSING_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 토큰 추출 및 검증
        token = extract_token_from_header(request)
        if not token:
            return Response({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error': 'MISSING_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 토큰 검증
        user_data = get_user_from_token(token)
        if not user_data:
            return Response({
                'success': False,
                'message': '토큰이 만료되었거나 유효하지 않습니다.',
                'error': 'INVALID_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 관리자 권한 확인 (auth='Y')
        if user_data[8] != 'Y':  # user_data[8]은 auth 필드
            return Response({
                'success': False,
                'message': '관리자 권한이 필요합니다.',
                'error': 'ADMIN_REQUIRED'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 필터 파라미터 파싱
            filter_param = request.GET.get('filter', '')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            
            # 기본 쿼리
            base_query = """
                SELECT user_id, user_login_id, name, dept, rank, email, 
                       created_dt, use_yn, auth
                FROM user_info 
                WHERE use_yn = 'Y'
            """
            params = []
            
            # 필터 적용
            if filter_param and ':' in filter_param:
                field, value = filter_param.split(':', 1)
                field = field.strip()
                value = value.strip()
                
                # 허용된 필드만 필터링
                allowed_fields = ['dept', 'name', 'user_login_id', 'rank', 'email']
                if field in allowed_fields:
                    base_query += f" AND {field} ILIKE %s"
                    params.append(f'%{value}%')
            
            # 전체 개수 조회
            count_query = f"SELECT COUNT(*) FROM ({base_query}) as count_table"
            with connection.cursor() as cursor:
                cursor.execute(count_query, params)
                total_count = cursor.fetchone()[0]
            
            # 페이지네이션 적용
            offset = (page - 1) * page_size
            base_query += " ORDER BY created_dt DESC LIMIT %s OFFSET %s"
            params.extend([page_size, offset])
            
            # 실제 데이터 조회
            with connection.cursor() as cursor:
                cursor.execute(base_query, params)
                users = cursor.fetchall()
            
            # 응답 데이터 구성
            user_list = []
            for user in users:
                user_list.append({
                    'user_id': str(user[0]),  # UUID를 문자열로 변환
                    'user_login_id': user[1],
                    'name': user[2],
                    'dept': user[3] or '',
                    'rank': user[4] or '',
                    'email': user[5] or '',
                    'created_dt': user[6].isoformat() if user[6] else '',
                    'use_yn': user[7],
                    'auth': user[8]
                })
            
            total_pages = (total_count + page_size - 1) // page_size
            
            return Response({
                'success': True,
                'message': '회원 목록을 성공적으로 조회했습니다.',
                'data': {
                    'users': user_list,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'current_page': page,
                    'page_size': page_size
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"회원 목록 조회 중 오류: {e}")
            return Response({
                'success': False,
                'message': '회원 목록 조회 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
