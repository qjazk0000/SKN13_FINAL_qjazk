from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
import os

logger = logging.getLogger(__name__)


class ReceiptUploadView(APIView):
    """
    1. 영수증 파일 업로드 + OCR 데이터 추출
    - file_info, receipt_info 테이블에 저장
    - status = pending
    - S3에도 업로드
    """
    @require_auth
    def post(self, request):
        serializer = ReceiptUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '입력 데이터가 유효하지 않습니다',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        f = serializer.validated_data['files']  # 단일 파일만 처리
        try:
            # 업로드된 파일을 임시 경로에 저장
            tmp_path = f"/tmp/{uuid.uuid4()}_{f.name}"
            with open(tmp_path, "wb") as tmp:
                for chunk in f.chunks():
                    tmp.write(chunk)

            # OCR 처리
            extracted_data = extract_receipt_info(tmp_path)
            store_name = extracted_data.get('storeName', '')
            payment_date = extracted_data.get('transactionDate', "").split()[0] or None
            amount = extracted_data.get('transactionAmount', 0)

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
                
                # file_info 저장 (S3 키 포함)
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
                cursor.execute("""
                    INSERT INTO receipt_info 
                    (receipt_id, file_id, user_id, payment_date, amount, currency, store_name, extracted_text, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', NOW(), NOW())
                """, [
                    receipt_id,
                    file_id,
                    request.user_id,
                    payment_date,
                    amount,
                    'KRW',
                    store_name,
                    str(extracted_data)
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
                    'extracted': extracted_data
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"파일 업로드/OCR 처리 오류: {str(e)}")
            # 임시 파일 정리
            try:
                if 'tmp_path' in locals():
                    os.unlink(tmp_path)
            except:
                pass
            return Response({
                'success': False,
                'message': '파일 업로드 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReceiptSaveView(APIView):
    """
    2. 사용자가 확인 후 최종 저장 → status를 processed로 변경
    """
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
            file_id = serializer.validated_data['file_id']
            store_name = serializer.validated_data['store_name']
            payment_date = serializer.validated_data['payment_date']
            amount = serializer.validated_data['amount']
            extracted_text = {
                "결제처": store_name,
                "결제일시": str(payment_date),
                "총합계": float(amount),
                "카드정보": serializer.validated_data.get('card_info', ''),
                "품목": serializer.validated_data.get('items', [])
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
                'message': '영수증 데이터가 최종 저장되었습니다.'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"영수증 저장 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '영수증 저장 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReceiptDownloadView(APIView):
    """
    3. CSV 다운로드
    """
    @require_auth
    def get(self, request):
        serializer = ReceiptDownloadSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '입력 데이터가 올바르지 않습니다.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        start = serializer.validated_data['start_date'] + '-01'
        end = serializer.validated_data['end_date'] + '-01'

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
