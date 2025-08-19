# adminapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from .serializers import (
    UserSearchSerializer,
    ConversationSearchSerializer,
    ReportedConversationSerializer,
    ReceiptSerializer,
    ReceiptDetailSerializer
)
# from authapp.decorators import admin_required
from .decorators import admin_required
import logging

logger = logging.getLogger(__name__)

######################################
# 회원 관리 기능
######################################
class UserManagementView(APIView):
    """
    관리자용 회원 조회 및 검색 API
    - 검색 유형: 전체/부서/이름/ID/직급/이메일
    - 검색어 입력 필드 지원
    """
    
    @admin_required
    def post(self, request):
        """
        회원 검색 처리
        - 입력: search_type, search_keyword
        - 출력: 검색된 회원 목록
        """
        serializer = UserSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            search_type = serializer.validated_data['search_type']
            keyword = serializer.validated_data.get('search_keyword', '')
            
            with connection.cursor() as cursor:
                # 기본 쿼리 (모든 회원)
                query = "SELECT * FROM user_info WHERE 1=1"
                params = []
                
                # 검색 타입에 따른 조건 추가
                if search_type != 'all' and keyword:
                    if search_type == 'dept':
                        query += " AND dept LIKE %s"  # 부서명 검색
                    elif search_type == 'name':
                        query += " AND name LIKE %s"  # 이름 검색
                    elif search_type == 'id':
                        query += " AND user_login_id LIKE %s"  # 로그인 ID 검색
                    elif search_type == 'rank':
                        query += " AND rank LIKE %s"  # 직급 검색
                    elif search_type == 'email':
                        query += " AND email LIKE %s"  # 이메일 검색
                    params.append(f'%{keyword}%')  # 부분 일치 검색
                
                # 쿼리 실행
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]  # 컬럼명 추출
                users = [dict(zip(columns, row)) for row in cursor.fetchall()]  # 딕셔너리 변환
                
                return Response({
                    'success': True,
                    'data': users  # 검색 결과 반환
                })
                
        except Exception as e:
            logger.error(f"회원 검색 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '회원 검색 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

######################################
# 대화 신고 내역 관리
######################################
class ConversationReportView(APIView):
    """
    신고된 대화 내역 조회 API
    - 기간 선택: 전체/오늘/일주일/직접입력
    - 검색 유형: 채팅ID/사용자ID/세션ID
    """
    
    @admin_required
    def post(self, request):
        """
        신고 대화 검색 처리
        - 입력: period, start_date, end_date, search_type, search_keyword
        - 출력: 필터링된 신고 목록
        """
        serializer = ConversationSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            period = serializer.validated_data['period']
            search_type = serializer.validated_data['search_type']
            keyword = serializer.validated_data.get('search_keyword', '')
            
            with connection.cursor() as cursor:
                query = "SELECT * FROM reported_conversation WHERE 1=1"
                params = []
                
                # 기간 필터링
                if period == 'today':
                    query += " AND DATE(created_at) = CURRENT_DATE"  # 오늘 데이터
                elif period == 'week':
                    query += " AND created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)"  # 최근 1주일
                elif period == 'custom' and serializer.validated_data.get('start_date'):
                    query += " AND DATE(created_at) BETWEEN %s AND %s"  # 사용자 지정 기간
                    params.extend([
                        serializer.validated_data['start_date'],
                        serializer.validated_data.get('end_date', serializer.validated_data['start_date'])
                    ])
                
                # 검색 타입 적용
                if keyword:
                    if search_type == 'chat_id':
                        query += " AND chat_id LIKE %s"  # 채팅 ID 검색
                    elif search_type == 'user_id':
                        query += " AND user_id LIKE %s"  # 사용자 ID 검색
                    elif search_type == 'session_id':
                        query += " AND session_id LIKE %s"  # 세션 ID 검색
                    params.append(f'%{keyword}%')
                
                query += " ORDER BY created_at DESC"  # 최신순 정렬
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                reports = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                return Response({
                    'success': True,
                    'data': reports
                })
                
        except Exception as e:
            logger.error(f"신고 대화 검색 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '신고 대화 검색 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

######################################
# 영수증 관리
######################################
class ReceiptManagementView(APIView):
    """
    영수증 목록 조회 API
    - 영수증 이미지, 파일명, 업로드 일시 정보 제공
    """
    
    @admin_required
    def get(self, request):
        """
        영수증 전체 목록 조회
        - 출력: 영수증 기본 정보 목록
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT receipt_id, user_id, file_name, uploaded_at, is_verified 
                    FROM receipt_info 
                    ORDER BY uploaded_at DESC
                """)
                columns = [col[0] for col in cursor.description]
                receipts = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                serializer = ReceiptSerializer(receipts, many=True)
                return Response({
                    'success': True,
                    'data': serializer.data  # 시리얼라이즈된 데이터 반환
                })
                
        except Exception as e:
            logger.error(f"영수증 목록 조회 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '영수증 목록 조회 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReceiptPreviewView(APIView):
    """
    영수증 상세 조회(미리보기) API
    - 특정 영수증의 이미지 URL과 추출된 텍스트 제공
    """
    
    @admin_required
    def get(self, request, receipt_id):
        """
        영수증 상세 정보 조회
        - 입력: receipt_id (경로 파라미터)
        - 출력: 영수증 이미지 URL과 추출 텍스트
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM receipt_info 
                    WHERE receipt_id = %s
                """, [receipt_id])
                row = cursor.fetchone()
                
                if not row:
                    return Response({
                        'success': False,
                        'message': '영수증을 찾을 수 없습니다'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                receipt = dict(zip(columns, row))  # 단일 영수증 정보 딕셔너리 변환
                serializer = ReceiptDetailSerializer(receipt)
                
                return Response({
                    'success': True,
                    'data': serializer.data  # 상세 정보 반환 (이미지 URL 포함)
                })
                
        except Exception as e:
            logger.error(f"영수증 상세 조회 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '영수증 상세 조회 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)