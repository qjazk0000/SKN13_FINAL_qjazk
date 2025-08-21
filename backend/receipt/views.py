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
import csv
import io
import uuid
import logging

logger = logging.getLogger(__name__)


class ReceiptUploadView(APIView):
    @require_auth
    def post(self, request):
        serializer = ReceiptUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({...}, status=status.HTTP_400_BAD_REQUEST)

        files = serializer.validated_data['files']
        results = []

        try:
            for f in files:
                # 업로드된 파일을 임시 경로에 저장
                tmp_path = f"/tmp/{f.name}"
                with open(tmp_path, "wb") as tmp:
                    for chunk in f.chunks():
                        tmp.write(chunk)

                # OCR 처리
                extracted_data = extract_receipt_info(tmp_path)

                with connection.cursor() as cursor:
                    file_id = uuid.uuid4()
                    receipt_id = uuid.uuid4()
                    
                    # file_info 저장
                    cursor.execute("""INSERT INTO file_info ...""", [...])

                    # receipt_info 저장
                    cursor.execute("""INSERT INTO receipt_info ...""", [
                        receipt_id,
                        file_id,
                        request.user_id,
                        extracted_data.get('결제일시'),
                        extracted_data.get('총합계', 0),
                        'KRW',
                        extracted_data.get('결제처'),
                        str(extracted_data)
                    ])

                    results.append({
                        'receipt_id': str(receipt_id),
                        'file_id': str(file_id),
                        'file_name': f.name,
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
            writer.writerow(['결제처', '결제일시', '총합계', '추출데이터'])

            for row in rows:
                writer.writerow([row[0], row[1], row[2], row[3]])

            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="receipts_{start}_{end}.csv"'
            return response

        except Exception as e:
            logger.error(f"CSV 다운로드 오류: {str(e)}")
            return Response({
                'success': False,
                'message': 'CSV 다운로드 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
