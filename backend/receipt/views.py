from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.http import HttpResponse
from authapp.utils import extract_token_from_header, get_user_from_token
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
import os
import logging

logger = logging.getLogger(__name__)


class ReceiptUploadView(APIView):
    def post(self, request):
        # 인증 확인
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
                'message': '토큰이 만료되었거나 유효하지 않습니다.',
                'error': 'INVALID_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # request 객체에 사용자 정보 추가
        request.user_id = user_data[0]
        serializer = ReceiptUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({...}, status=status.HTTP_400_BAD_REQUEST)

        files = serializer.validated_data['files']
        results = []

        try:
            for f in files:
                # S3에 파일 업로드
                upload_result = s3_receipt_service.upload_receipt_file(f, request.user_id)
                
                if not upload_result['success']:
                    logger.error(f"파일 업로드 실패: {upload_result['error']}")
                    continue

                # OCR 처리 (S3에서 다운로드하여 처리)
                extracted_data = extract_receipt_info(f)  # 파일 객체 직접 전달

                with connection.cursor() as cursor:
                    file_id = uuid.uuid4()
                    receipt_id = uuid.uuid4()
                    
                    # file_info 저장 (S3 키 포함)
                    cursor.execute("""
                        INSERT INTO file_info (file_id, file_origin_name, file_name, file_path, file_size, file_ext, uploaded_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """, [
                        file_id,
                        upload_result['original_name'],
                        upload_result['original_name'],
                        upload_result['s3_key'],  # S3 키를 file_path에 저장
                        upload_result['file_size'],
                        os.path.splitext(upload_result['original_name'])[1]
                    ])

                    # receipt_info 저장
                    cursor.execute("""
                        INSERT INTO receipt_info (receipt_id, file_id, user_id, payment_date, amount, currency, store_name, extracted_text, status, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """, [
                        receipt_id,
                        file_id,
                        request.user_id,
                        extracted_data.get('결제일시'),
                        extracted_data.get('총합계', 0),
                        'KRW',
                        extracted_data.get('결제처'),
                        str(extracted_data),
                        'pending'
                    ])

                    results.append({
                        'receipt_id': str(receipt_id),
                        'file_id': str(file_id),
                        'file_name': upload_result['original_name'],
                        's3_key': upload_result['s3_key'],
                        'file_url': upload_result['file_url'],
                        'extracted': extracted_data
                    })

            return Response({
                'success': True,
                'message': '파일 업로드 및 OCR 추출 성공',
                'data': results
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"파일 업로드/OCR 처리 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '파일 업로드 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReceiptSaveView(APIView):
    """
    2. 사용자가 확인 후 최종 저장 → status를 processed로 변경
    """
    def post(self, request):
        # 인증 확인
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
                'message': '토큰이 만료되었거나 유효하지 않습니다.',
                'error': 'INVALID_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # request 객체에 사용자 정보 추가
        request.user_id = user_data[0]
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
    def get(self, request):
        # 인증 확인
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
                'message': '토큰이 만료되었거나 유효하지 않습니다.',
                'error': 'INVALID_TOKEN'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # request 객체에 사용자 정보 추가
        request.user_id = user_data[0]
        serializer = ReceiptDownloadSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '입력 데이터가 올바르지 않습니다.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        start = serializer.validated_data['start_date']
        end = serializer.validated_data['end_date']

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
