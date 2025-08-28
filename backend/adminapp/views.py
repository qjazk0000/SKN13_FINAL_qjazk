from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from authapp.utils import extract_token_from_header, get_user_from_token
import os

from .serializers import (
    UserSearchSerializer,
    ConversationSearchSerializer,
    AdminReceiptSerializer,
    AdminReceiptDetailSerializer,
    ReceiptPreviewSerializer,
)
from .decorators import admin_required

import logging

logger = logging.getLogger(__name__)

def generate_s3_public_url(s3_key):
    """
    S3 키를 공개 URL로 변환
    """
    if not s3_key:
        return ""
    
    # S3 버킷 정보 (환경변수에서 가져오거나 하드코딩)
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'skn.dopamine-navi.bucket')
    region = os.getenv('AWS_REGION', 'ap-northeast-2')
    
    # S3 공개 URL 형식: https://bucket-name.s3.region.amazonaws.com/key
    s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
    return s3_url

class AdminUsersView(APIView):
    """
    관리자용 회원 조회 API
    GET /api/admin/users?filter={field}:{value}
    """
    
    def get(self, request):
        # Authorization 헤더에서 토큰 추출
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


class AdminReceiptsView(APIView):
    def _parse_items_info(self, extracted_text):
        """
        추출된 텍스트에서 품목 정보를 파싱하여 반환
        """
        try:
            import json
            import ast
            import re
            
            logger.info(f"_parse_items_info 호출됨, extracted_text: {extracted_text}")
            logger.info(f"extracted_text 타입: {type(extracted_text)}")
            
            if not extracted_text:
                logger.info("extracted_text가 비어있음")
                return []
            
            data = None
            
            # extracted_text가 문자열인 경우 파싱
            if isinstance(extracted_text, str):
                logger.info("문자열 형태의 extracted_text 파싱 시도")
                
                # 먼저 JSON으로 파싱 시도
                try:
                    data = json.loads(extracted_text)
                    logger.info(f"JSON 파싱 성공: {data}")
                except json.JSONDecodeError as e:
                    logger.info(f"JSON 파싱 실패: {e}")
                    
                    # JSON 실패 시 ast.literal_eval로 파싱 시도 (Python 딕셔너리 형태)
                    try:
                        data = ast.literal_eval(extracted_text)
                        logger.info(f"ast.literal_eval 파싱 성공: {data}")
                    except (ValueError, SyntaxError) as e:
                        logger.info(f"ast.literal_eval 파싱 실패: {e}")
                        
                        # 정규표현식으로 '품목' 키와 배열 추출 시도
                        try:
                            # '품목': [...] 패턴 찾기
                            pattern = r"'품목':\s*\[(.*?)\]"
                            match = re.search(pattern, extracted_text, re.DOTALL)
                            if match:
                                items_str = match.group(1)
                                logger.info(f"정규표현식으로 추출된 items_str: {items_str}")
                                
                                # 간단한 파싱으로 품목 정보 추출
                                items = []
                                # {'productName': '...', 'quantity': ...} 패턴 찾기
                                item_pattern = r"\{'productName':\s*'([^']+)',\s*'quantity':\s*(\d+)[^}]*\}"
                                item_matches = re.findall(item_pattern, items_str)
                                
                                for product_name, quantity in item_matches:
                                    items.append({
                                        'productName': product_name,
                                        'quantity': int(quantity)
                                    })
                                
                                data = {'품목': items}
                                logger.info(f"정규표현식으로 파싱된 데이터: {data}")
                            else:
                                logger.error(f"정규표현식으로도 파싱 실패: {extracted_text}")
                                return []
                        except Exception as e:
                            logger.error(f"정규표현식 파싱 오류: {e}")
                            return []
            else:
                data = extracted_text
                logger.info(f"이미 딕셔너리 형태: {data}")
            
            if not data:
                logger.error("파싱된 데이터가 없음")
                return []
            
            # '품목' 키에서 품목 정보 추출
            items = data.get('품목', [])
            logger.info(f"추출된 품목 배열: {items}")
            
            if not items:
                logger.info("품목 배열이 비어있음")
                return []
            
            # 품목명과 갯수를 문자열로 포맷팅
            formatted_items = []
            for item in items:
                product_name = item.get('productName', '')
                quantity = item.get('quantity', 1)
                if product_name:
                    formatted_items.append(f"{product_name} x{quantity}")
            
            logger.info(f"최종 포맷된 품목 목록: {formatted_items}")
            return formatted_items
            
        except Exception as e:
            logger.error(f"품목 정보 파싱 오류: {str(e)}")
            logger.error(f"extracted_text 전체 내용: {extracted_text}")
            return []
    
    def get(self, request):
        # Authorization 헤더에서 토큰 추출
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
            # 쿼리 파라미터 파싱
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            reported_yn = request.GET.get('reported_yn')
            name_filter = request.GET.get('name')
            dept_filter = request.GET.get('dept')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            
            # 기본 쿼리 (JOIN으로 필요한 정보 가져오기)
            base_query = """
                SELECT 
                    u.name,
                    u.dept,
                    r.created_at,
                    r.amount,
                    r.status,
                    f.file_path,
                    r.receipt_id,
                    u.user_login_id,
                    r.extracted_text
                FROM receipt_info r
                JOIN user_info u ON r.user_id = u.user_id
                JOIN file_info f ON r.file_id = f.file_id
                WHERE u.use_yn = 'Y'
            """
            params = []
            
            # 날짜 필터 적용
            if start_date:
                base_query += " AND r.created_at >= %s"
                params.append(start_date)
            
            if end_date:
                base_query += " AND r.created_at <= %s"
                params.append(end_date + ' 23:59:59')  # 해당 날짜의 마지막 시간까지
            
            # 이름 필터 적용
            if name_filter:
                base_query += " AND u.name ILIKE %s"
                params.append(f'%{name_filter}%')
            
            # 부서 필터 적용
            if dept_filter:
                base_query += " AND u.dept ILIKE %s"
                params.append(f'%{dept_filter}%')
            
            # 신고 여부 필터 적용
            if reported_yn:
                base_query += " AND r.status = %s"
                params.append(reported_yn)
            
            # 전체 개수 조회
            count_query = f"SELECT COUNT(*) FROM ({base_query}) as count_table"
            with connection.cursor() as cursor:
                cursor.execute(count_query, params)
                total_count = cursor.fetchone()[0]
            
            # 페이지네이션 적용
            offset = (page - 1) * page_size
            base_query += " ORDER BY r.created_at DESC LIMIT %s OFFSET %s"
            params.extend([page_size, offset])
            
            # 실제 데이터 조회
            with connection.cursor() as cursor:
                cursor.execute(base_query, params)
                receipts = cursor.fetchall()
            
            # 응답 데이터 구성
            receipt_list = []
            for receipt in receipts:
                # 품목 정보 파싱
                items_info = self._parse_items_info(receipt[8])  # extracted_text는 인덱스 8
                
                receipt_list.append({
                    'name': receipt[0] or '',
                    'dept': receipt[1] or '',
                    'created_at': receipt[2].isoformat() if receipt[2] else '',
                    'amount': float(receipt[3]) if receipt[3] else 0,
                    'status': receipt[4] or '',
                    'file_path': generate_s3_public_url(receipt[5]) if receipt[5] else '',
                    'receipt_id': str(receipt[6]),
                    'user_login_id': receipt[7] or '',
                    'extracted_text': receipt[8] or '',
                    'items_info': items_info
                })
            
            total_pages = (total_count + page_size - 1) // page_size
            
            return Response({
                'success': True,
                'message': '영수증 목록을 성공적으로 조회했습니다.',
                'data': {
                    'receipts': receipt_list,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'current_page': page,
                    'page_size': page_size
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"영수증 목록 조회 중 오류: {e}")
            return Response({
                'success': False,
                'message': '영수증 목록 조회 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    
    def _parse_items_info(self, extracted_text):
        """
        추출된 텍스트에서 품목 정보를 파싱하여 반환
        """
        try:
            import json
            import ast
            import re
            
            logger.info(f"_parse_items_info 호출됨, extracted_text: {extracted_text}")
            logger.info(f"extracted_text 타입: {type(extracted_text)}")
            
            if not extracted_text:
                logger.info("extracted_text가 비어있음")
                return []
            
            data = None
            
            # extracted_text가 문자열인 경우 파싱
            if isinstance(extracted_text, str):
                logger.info("문자열 형태의 extracted_text 파싱 시도")
                
                # 먼저 JSON으로 파싱 시도
                try:
                    data = json.loads(extracted_text)
                    logger.info(f"JSON 파싱 성공: {data}")
                except json.JSONDecodeError as e:
                    logger.info(f"JSON 파싱 실패: {e}")
                    
                    # JSON 실패 시 ast.literal_eval로 파싱 시도 (Python 딕셔너리 형태)
                    try:
                        data = ast.literal_eval(extracted_text)
                        logger.info(f"ast.literal_eval 파싱 성공: {data}")
                    except (ValueError, SyntaxError) as e:
                        logger.info(f"ast.literal_eval 파싱 실패: {e}")
                        
                        # 정규표현식으로 '품목' 키와 배열 추출 시도
                        try:
                            # '품목': [...] 패턴 찾기
                            pattern = r"'품목':\s*\[(.*?)\]"
                            match = re.search(pattern, extracted_text, re.DOTALL)
                            if match:
                                items_str = match.group(1)
                                logger.info(f"정규표현식으로 추출된 items_str: {items_str}")
                                
                                # 간단한 파싱으로 품목 정보 추출
                                items = []
                                # {'productName': '...', 'quantity': ...} 패턴 찾기
                                item_pattern = r"\{'productName':\s*'([^']+)',\s*'quantity':\s*(\d+)[^}]*\}"
                                item_matches = re.findall(item_pattern, items_str)
                                
                                for product_name, quantity in item_matches:
                                    items.append({
                                        'productName': product_name,
                                        'quantity': int(quantity)
                                    })
                                
                                data = {'품목': items}
                                logger.info(f"정규표현식으로 파싱된 데이터: {data}")
                            else:
                                logger.error(f"정규표현식으로도 파싱 실패: {extracted_text}")
                                return []
                        except Exception as e:
                            logger.error(f"정규표현식 파싱 오류: {e}")
                            return []
            else:
                data = extracted_text
                logger.info(f"이미 딕셔너리 형태: {data}")
            
            if not data:
                logger.error("파싱된 데이터가 없음")
                return []
            
            # '품목' 키에서 품목 정보 추출
            items = data.get('품목', [])
            logger.info(f"추출된 품목 배열: {items}")
            
            if not items:
                logger.info("품목 배열이 비어있음")
                return []
            
            # 품목명과 갯수를 문자열로 포맷팅
            formatted_items = []
            for item in items:
                product_name = item.get('productName', '')
                quantity = item.get('quantity', 1)
                if product_name:
                    formatted_items.append(f"{product_name} x{quantity}")
            
            logger.info(f"최종 포맷된 품목 목록: {formatted_items}")
            return formatted_items
            
        except Exception as e:
            logger.error(f"품목 정보 파싱 오류: {str(e)}")
            logger.error(f"extracted_text 전체 내용: {extracted_text}")
            return []
    
    @admin_required
    def get(self, request):
        """
        영수증 전체 목록 조회
        - 출력: 영수증 기본 정보 목록
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT r.receipt_id, r.user_id, r.store_name, r.payment_date, r.amount, 
                           r.extracted_text, r.status, r.created_at, r.updated_at,
                           f.file_origin_name, f.file_path,
                           u.name, u.dept
                    FROM receipt_info r
                    LEFT JOIN file_info f ON r.file_id = f.file_id
                    LEFT JOIN user_info u ON r.user_id = u.user_id
                    ORDER BY r.created_at DESC
                """)
                columns = [col[0] for col in cursor.description]
                receipts = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                # 디버깅: 원본 데이터 확인
                logger.info(f"조회된 영수증 개수: {len(receipts)}")
                for i, receipt in enumerate(receipts):
                    logger.info(f"영수증 {i+1} 원본 데이터: {receipt}")
                    logger.info(f"영수증 {i+1} extracted_text: {receipt.get('extracted_text')}")
                
                # 품목 정보를 직접 처리하여 추가
                for receipt in receipts:
                    receipt['items_info'] = self._parse_items_info(receipt.get('extracted_text'))
                    # 테스트용으로 하드코딩된 값 추가
                    receipt['test_items'] = ['테스트 품목1 x2', '테스트 품목2 x1']
                    logger.info(f"처리된 영수증: {receipt}")
                
                # Serializer 없이 직접 반환하여 테스트
                return Response({
                    'success': True,
                    'data': {
                        'receipts': receipts,  # serializer.data 대신 원본 데이터 직접 반환
                        'total_pages': 1
                    }
                })
                
        except Exception as e:
            logger.error(f"영수증 목록 조회 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '영수증 목록 조회 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminReceiptDetailView(APIView):
    """
    관리자용 영수증 상세 조회 API
    - 영수증 상세 정보 제공
    """
    
    @admin_required
    def get(self, request, receipt_id):
        """
        영수증 상세 정보 조회
        - 입력: receipt_id (경로 파라미터)
        - 출력: 영수증 상세 정보
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT ri.*, fi.file_origin_name, fi.file_path
                    FROM receipt_info ri
                    JOIN file_info fi ON ri.file_id = fi.file_id
                    WHERE ri.receipt_id = %s
                """, [receipt_id])
                
                row = cursor.fetchone()
                if not row:
                    return Response({
                        'success': False,
                        'message': '영수증을 찾을 수 없습니다'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                receipt = dict(zip(columns, row))
                
                # 새로운 상세 시리얼라이저 사용
                serializer = AdminReceiptDetailSerializer(receipt) #ReceiptDetailSerializer(receipt)
                return Response({
                    'success': True,
                    'data': serializer.data
                })
                
        except Exception as e:
            logger.error(f"영수증 상세 조회 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '영수증 상세 조회 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReceiptPreviewView(APIView):
    """
    영수증 이미지 미리보기 API
    - 특정 영수증의 이미지 URL 제공
    """
    
    @admin_required
    def get(self, request, receipt_id):
        """
        영수증 이미지 미리보기
        - 입력: receipt_id (경로 파라미터)
        - 출력: 영수증 이미지 URL
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT fi.file_origin_name, fi.file_path
                    FROM receipt_info ri
                    JOIN file_info fi ON ri.file_id = fi.file_id
                    WHERE ri.receipt_id = %s
                """, [receipt_id])
                
                row = cursor.fetchone()
                if not row:
                    return Response({
                        'success': False,
                        'message': '영수증을 찾을 수 없습니다'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                file_info = dict(zip(columns, row))
                
                # 이미지 미리보기 시리얼라이저 사용
                serializer = ReceiptPreviewSerializer(file_info)
                return Response({
                    'success': True,
                    'data': serializer.data
                })
                
        except Exception as e:
            logger.error(f"영수증 미리보기 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '영수증 미리보기 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
