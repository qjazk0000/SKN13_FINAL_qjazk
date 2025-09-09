from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.db import connection
from django.http import HttpResponse
from authapp.decorators import require_auth
from .serializers import (
    ReceiptUploadSerializer,
    ReceiptSaveSerializer,
    ReceiptDownloadSerializer
)
from .utils import extract_receipt_info
from .services import s3_receipt_service
import csv
import io
import uuid
import logging
from datetime import datetime
import os
import re
import calendar
from zipfile import ZipFile

logger = logging.getLogger(__name__)

class ReceiptListView(generics.ListAPIView):
    """
    영수증 목록 조회 (페이징)
    """
    @require_auth
    def get(self, request):
        user_id = request.user_id
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        offset = (page - 1) * page_size

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT receipt_id, file_id, status, created_at, store_name, amount
                    FROM receipt_info
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, [user_id, page_size, offset])
                rows = cursor.fetchall()

                cursor.execute("""
                    SELECT COUNT(*) FROM receipt_info WHERE user_id = %s
                """, [user_id])
                total_count = cursor.fetchone()[0]
            
            receipts = [
                {
                    "receipt_id": row[0],
                    "file_id": row[1],
                    "status": row[2],
                    "created_at": row[3],
                    "store_name": row[4],
                    "amount": row[5],
                }
                for row in rows
            ]
            
            return Response({
                'success': True,
                'data': {
                    'receipts': receipts,
                    'total_count': total_count,
                    'page': page,
                    'page_size': page_size
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"영수증 목록 조회 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '영수증 목록 조회 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReceiptUploadView(APIView):
    """
    1. 영수증 파일 업로드 + OCR 데이터 추출
    - file_info, receipt_info 테이블에 저장
    - status = pending
    - S3에도 업로드
    """
    authentication_classes = []  # 커스텀 JWT 인증을 사용하므로 DRF 인증 비활성화
    permission_classes = []      # 권한 검사는 데코레이터에서 수행
    
    @require_auth
    def post(self, request):
        serializer = ReceiptUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '입력 데이터가 유효하지 않습니다',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        f = serializer.validated_data['files']
        results = []

        # zip 파일 처리
        if f.name.lower().endswith('.zip'):
            tmp_zip_path = f"/tmp/{uuid.uuid4()}_{f.name}"
            with open(tmp_zip_path, "wb") as tmp:
                for chunk in f.chunks():
                    tmp.write(chunk)
            with ZipFile(tmp_zip_path, 'r') as zip_ref:
                image_names = [name for name in zip_ref.namelist() if name.lower().endswith(('.jpg', '.jpeg', '.png'))]
                for img_name in image_names:
                    with zip_ref.open(img_name) as img_file:
                        tmp_img_path = f"/tmp/{uuid.uuid4()}_{img_name}"
                        with open(tmp_img_path, "wb") as out_img:
                            out_img.write(img_file.read())
                        # OCR 처리
                        extracted_data = extract_receipt_info(tmp_img_path)
                        store_name = extracted_data.get('storeName', '')
                        payment_date = normalize_date(extracted_data.get('transactionDate', ""))
                        amount = extracted_data.get('transactionAmount', 0)
                        card_info = extracted_data.get('cardNumber', '')
                        items = extracted_data.get('items', [])

                        # 품목 배열을 한글 키로 변환
                        converted_items = []
                        for item in items:
                            converted_items.append({
                                "품명": item.get("productName", ""),
                                "단가": item.get("unitPrice", 0),
                                "수량": item.get("quantity", 1),
                                "금액": item.get("totalPrice", 0)
                            })

                        # 전체 OCR 데이터를 한글 키로 통일
                        normalized_extracted = {
                            "결제처": store_name,
                            "결제일시": str(payment_date),
                            "총합계": float(amount),
                            "카드정보": card_info,
                            "품목": converted_items
                        }

                        # S3에 임시 파일 업로드
                        with open(tmp_img_path, 'rb') as tmp_file:
                            s3_upload_result = s3_receipt_service.upload_receipt_file(tmp_file, request.user_id)
                        
                        if not s3_upload_result['success']:
                            logger.error(f"S3 업로드 실패: {s3_upload_result['error']}")
                            return Response({
                                'success': False,
                                'message': f'S3 업로드 실패: {s3_upload_result["error"]}',
                                'error': 'S3_UPLOAD_FAILED'
                            }, status=status.HTTP_400_BAD_REQUEST)

                        # file_info / receipt_info 저장
                        with connection.cursor() as cursor:
                            file_id = uuid.uuid4()
                            receipt_id = uuid.uuid4()                
                            cursor.execute("""
                                INSERT INTO file_info 
                                (file_id, chat_id, file_origin_name, file_name, file_path, file_size, file_ext, uploaded_at)
                                VALUES (%s, NULL, %s, %s, %s, %s, %s, NOW())
                            """, [
                                file_id,
                                f.name,
                                f"receipt_{file_id}",
                                s3_upload_result['s3_key'],  # S3 키를 file_path에 저장
                                f.size,
                                f.name.split('.')[-1] if '.' in f.name else ''
                            ])

                            # receipt_info 저장 (status = pending)
                            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute("""
                                INSERT INTO receipt_info 
                                (receipt_id, file_id, user_id, payment_date, amount, currency, store_name, extracted_text, status, created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s, %s)
                            """, [
                                receipt_id,
                                file_id,
                                request.user_id,
                                payment_date,
                                amount,
                                'KRW',
                                store_name,
                                str(normalized_extracted),   # 한글화된 OCR 데이터 저장
                                now_str,
                                now_str
                            ])
                        # 결과 리스트에 추가
                        results.append({
                            'file_name': img_name,
                            'extracted': normalized_extracted,
                            'receipt_id': str(receipt_id),
                            'file_id': str(file_id),
                            's3_key': s3_upload_result['s3_key'],
                            'file_url': s3_upload_result['file_url'],
                        })
                        # 임시 이미지 파일 삭제
                        try:
                            os.unlink(tmp_img_path)
                        except Exception as e:
                            logger.warning(f"임시 이미지 파일 삭제 실패: {e}")
            os.unlink(tmp_zip_path)
            return Response({
                'success': True,
                'message': '여러 영수증 파일 처리 성공',
                'data': results
            }, status=status.HTTP_201_CREATED)
        else:
            try:
                # 업로드된 파일을 임시 경로에 저장
                tmp_path = f"/tmp/{uuid.uuid4()}_{f.name}"
                with open(tmp_path, "wb") as tmp:
                    for chunk in f.chunks():
                        tmp.write(chunk)

                # OCR 처리
                extracted_data = extract_receipt_info(tmp_path)
                store_name = extracted_data.get('storeName', '')
                payment_date = normalize_date(extracted_data.get('transactionDate', ""))
                amount = extracted_data.get('transactionAmount', 0)
                card_info = extracted_data.get('cardNumber', '')
                items = extracted_data.get('items', [])

                # 품목 배열을 한글 키로 변환
                converted_items = []
                for item in items:
                    converted_items.append({
                        "품명": item.get("productName", ""),
                        "단가": item.get("unitPrice", 0),
                        "수량": item.get("quantity", 1),
                        "금액": item.get("totalPrice", 0)
                    })

                # 전체 OCR 데이터를 한글 키로 통일
                normalized_extracted = {
                    "결제처": store_name,
                    "결제일시": str(payment_date),
                    "총합계": float(amount),
                    "카드정보": card_info,
                    "품목": converted_items
                }

                # S3에 임시 파일 업로드
                with open(tmp_path, 'rb') as tmp_file:
                    s3_upload_result = s3_receipt_service.upload_receipt_file(tmp_file, request.user_id)
                
                if not s3_upload_result['success']:
                    logger.error(f"S3 업로드 실패: {s3_upload_result['error']}")
                    return Response({
                        'success': False,
                        'message': f'S3 업로드 실패: {s3_upload_result["error"]}',
                        'error': 'S3_UPLOAD_FAILED'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # file_info / receipt_info 저장
                with connection.cursor() as cursor:
                    file_id = uuid.uuid4()
                    receipt_id = uuid.uuid4()                
                    cursor.execute("""
                        INSERT INTO file_info 
                        (file_id, chat_id, file_origin_name, file_name, file_path, file_size, file_ext, uploaded_at)
                        VALUES (%s, NULL, %s, %s, %s, %s, %s, NOW())
                    """, [
                        file_id,
                        f.name,
                        f"receipt_{file_id}",
                        s3_upload_result['s3_key'],  # S3 키를 file_path에 저장
                        f.size,
                        f.name.split('.')[-1] if '.' in f.name else ''
                    ])

                    # receipt_info 저장 (status = pending)
                    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute("""
                        INSERT INTO receipt_info 
                        (receipt_id, file_id, user_id, payment_date, amount, currency, store_name, extracted_text, status, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s, %s)
                    """, [
                        receipt_id,
                        file_id,
                        request.user_id,
                        payment_date,
                        amount,
                        'KRW',
                        store_name,
                        str(normalized_extracted),   # 한글화된 OCR 데이터 저장
                        now_str,
                        now_str
                    ])
                # 임시 파일 삭제
                try:
                    os.unlink(tmp_path)
                except Exception as e:
                    logger.warning(f"임시 파일 삭제 실패: {e}")

                return Response({
                    'success': True,
                    'message': '파일 업로드 및 OCR 추출 성공',
                    'data': {
                        'receipt_id': str(receipt_id),
                        'file_id': str(file_id),
                        'file_name': f.name,
                        's3_key': s3_upload_result['s3_key'],
                        'file_url': s3_upload_result['file_url'],
                        'extracted': normalized_extracted   # 프론트로도 한글 키 반환
                    }
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"파일 업로드/OCR 처리 오류: {str(e)}")
                # 임시 파일 정리
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except Exception as e2:
                        logger.warning(f"임시 파일 삭제 실패: {e2}")
                return Response({
                    'success': False,
                    'message': '파일 업로드 중 오류 발생'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ReceiptSaveView(APIView):
    """
    2. 사용자가 확인 후 최종 저장 → status를 processed로 변경
    """
    authentication_classes = []  # 커스텀 JWT 인증을 사용하므로 DRF 인증 비활성화
    permission_classes = []      # 권한 검사는 데코레이터에서 수행
    
    @require_auth
    def post(self, request):
        serializer = ReceiptSaveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '입력 데이터가 올바르지 않습니다.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            all_receipts = serializer.validated_data['receipts']
            for receipt in all_receipts:
                file_id = receipt['file_id']
                store_name = receipt['store_name']
                raw_payment_date = receipt['payment_date']
                payment_date = normalize_date(raw_payment_date)
                amount = receipt['amount']
                card_info = receipt.get('card_info', '')
                items = receipt.get('items', [])

                extracted_text = {
                    "결제처": store_name,
                    "결제일시": str(payment_date),
                    "총합계": float(amount),
                    "카드정보": card_info,
                    "품목": items,
                }

                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE receipt_info 
                        SET store_name = %s,
                            payment_date = %s,
                            amount = %s,
                            extracted_text = %s,
                            status = 'processed',
                            updated_at = NOW()
                        WHERE file_id = %s AND user_id = %s
                    """, [
                        store_name,
                        payment_date,
                        amount,
                        str(extracted_text),
                        file_id,
                        request.user_id
                    ])

            return Response({
                'success': True,
                'message': f'총 {len(all_receipts)}개의 영수증이 processed 처리되었습니다.'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"영수증 업로드 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '업로드 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReceiptDownloadView(APIView):
    """
    3. CSV 다운로드
    """
    authentication_classes = []  # 커스텀 JWT 인증을 사용하므로 DRF 인증 비활성화
    permission_classes = []      # 권한 검사는 데코레이터에서 수행
    
    @require_auth
    def get(self, request):
        serializer = ReceiptDownloadSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '입력 데이터가 올바르지 않습니다.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        start_year, start_month = map(int, serializer.validated_data['start_date'].split('-'))
        end_year, end_month = map(int, serializer.validated_data['end_date'].split('-'))

        if (start_year, start_month) > (end_year, end_month):
            return Response({
                'success': False,
                'message': '시작 월은 종료 월보다 이후일 수 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        start = f"{start_year}-{start_month:02d}-01"
        last_day = calendar.monthrange(end_year, end_month)[1]  # 마지막 날짜(예: 28, 29, 30, 31)
        end = f"{end_year}-{end_month:02d}-{last_day:02d}"

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT store_name, payment_date, amount, extracted_text, file_id
                    FROM receipt_info
                    WHERE user_id = %s AND payment_date BETWEEN %s AND %s
                    ORDER BY payment_date ASC
                """, [request.user_id, start, end])
                rows = cursor.fetchall()

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['결제처', '결제일시', '총합계', '추출데이터', '파일링크'])

            for row in rows:
                store_name, payment_date, amount, extracted_text, file_id = row
                
                # S3 파일 링크 생성
                file_link = ""
                if file_id:
                    with connection.cursor() as file_cursor:
                        file_cursor.execute("""
                            SELECT file_path FROM file_info WHERE file_id = %s
                        """, [file_id])
                        file_result = file_cursor.fetchone()
                        if file_result and file_result[0]:
                            s3_key = file_result[0]
                            # Presigned URL 생성 (1시간 유효)
                            file_link = s3_receipt_service.get_file_presigned_url(s3_key, expires_in=3600) or ""
                
                writer.writerow([store_name, payment_date, amount, extracted_text, file_link])

            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="receipts_{start}_{end}.csv"'
            return response

        except Exception as e:
            logger.error(f"CSV 다운로드 오류: {str(e)}")
            return Response({
                'success': False,
                'message': 'CSV 다운로드 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReceiptDetailView(APIView):
    """
    업로드된 영수증의 임시 OCR 데이터를 조회
    """
    @require_auth
    def get(self, request, receipt_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT store_name, payment_date, amount, extracted_text, status
                    FROM receipt_info
                    WHERE receipt_id = %s AND user_id = %s
                """, [receipt_id, request.user_id])
                row = cursor.fetchone()

            if not row:
                return Response({
                    'success': False,
                    'message': '영수증 데이터를 찾을 수 없습니다.'
                }, status=status.HTTP_404_NOT_FOUND)

            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, row))

            return Response({
                'success': True,
                'data': data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"영수증 조회 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '영수증 조회 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def normalize_date(date_str):
    """
    다양한 날짜 문자열을 'YYYY-MM-DD' 형태로 변환.
    변환 불가능하면 None 반환.
    """
    if not date_str or not isinstance(date_str, str):
        return None

    date_str = date_str.strip()

    # 1) 괄호 안의 요일(한글/영문) 제거: (월), (Tue), (수)
    date_str = re.sub(r'\([^)]*\)', '', date_str).strip()

    # 시도할 포맷들
    formats = [
        "%Y-%m-%d %H:%M:%S",  # 2024-02-13 08:23:13
        "%Y-%m-%d %H:%M",     # 2024-02-13 08:23
        "%Y-%m-%d",           # 2024-02-13
        "%Y/%m/%d",           # 2024/01/24
        "%Y.%m.%d",           # 2024.01.24
        "%Y%m%d",             # 20240213
        "%Y-%m%d",            # 2024-0213
        "%Y%m-%d",            # 202402-13
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")  # 최종 출력: YYYY-MM-DD
        except ValueError:
            continue

    # 어떤 포맷에도 맞지 않으면 None 반환
    return None