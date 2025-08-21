# receipt/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
import os
from adminapp.decorators import admin_required

class FileUploadView(APIView):
    """
    영수증 파일 업로드 API
    - 파일 업로드 및 임시 영수증 정보 생성
    """
    @admin_required
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '입력 데이터가 유효하지 않습니다',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            uploaded_file = serializer.validated_data['file']
            chat_id = serializer.validated_data.get('chat_id')
            
            # 파일 정보 저장
            with connection.cursor() as cursor:
                file_id = uuid.uuid4()
                
                # file_info 테이블에 저장
                cursor.execute("""
                    INSERT INTO file_info 
                    (file_id, chat_id, file_origin_name, file_name, file_path, file_size, file_ext, uploaded_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """, [
                    file_id,
                    chat_id,
                    uploaded_file.name,
                    f"receipt_{file_id}",
                    f"receipts/{file_id}",
                    uploaded_file.size,
                    uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else ''
                ])

                # receipt_info 테이블에 임시 데이터 생성 (OCR 처리 대기 상태)
                receipt_id = uuid.uuid4()
                cursor.execute("""
                    INSERT INTO receipt_info 
                    (receipt_id, file_id, user_id, payment_date, amount, currency, store_name, extracted_text, status, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), 0, 'KRW', '처리중', 'OCR 처리 중입니다...', 'processing', NOW(), NOW())
                """, [receipt_id, file_id, request.user_id])

                # TODO: 실제로는 여기서 OCR 처리 작업을 비동기로 실행
                # 임시로 2초 후에 더미 데이터로 업데이트 (실제 구현시 Celery 등 사용)
                def update_with_ocr_data():
                    with connection.cursor() as update_cursor:
                        update_cursor.execute("""
                            UPDATE receipt_info 
                            SET store_name = %s, payment_date = %s, 
                                amount = %s, extracted_text = %s, status = 'pending'
                            WHERE receipt_id = %s
                        """, [
                            '스타벅스 강남점',
                            '2024-01-15 14:30:00',
                            6500,
                            '스타벅스 강남점\n아메리카노: 4,500원\n카페라떼: 6,500원\n합계: 11,000원',
                            receipt_id
                        ])

                # 임시: 바로 OCR 데이터 설정 (실제는 비동기 처리)
                update_with_ocr_data()

                return Response({
                    'success': True,
                    'message': '파일 업로드 성공',
                    'data': {
                        'receipt_id': receipt_id,
                        'file_id': file_id
                    }
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"파일 업로드 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '파일 업로드 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ReceiptExtractionView(APIView):
    """
    영수증 텍스트 추출 결과 확인 API
    - 사용자가 업로드 후 추출된 정보 확인
    """
    @admin_required
    def get(self, request, receipt_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT ri.receipt_id, ri.store_name, ri.payment_date, 
                           ri.amount, ri.currency, ri.extracted_text,
                           fi.file_origin_name
                    FROM receipt_info ri
                    JOIN file_info fi ON ri.file_id = fi.file_id
                    WHERE ri.receipt_id = %s AND ri.user_id = %s
                """, [receipt_id, request.user_id])
                
                row = cursor.fetchone()
                if not row:
                    return Response({
                        'success': False,
                        'message': '영수증을 찾을 수 없습니다'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                receipt_data = dict(zip(columns, row))
                
                return Response({
                    'success': True,
                    'data': receipt_data
                })

        except Exception as e:
            logger.error(f"영수증 추출 정보 조회 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '영수증 정보 조회 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReceiptConfirmationView(APIView):
    """
    영수증 확인 및 최종 업로드 API
    - 사용자가 정보 확인 후 업로드 완료
    """
    @admin_required
    def post(self, request, receipt_id):
        serializer = ReceiptConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            is_confirmed = serializer.validated_data['is_confirmed']
            corrections = serializer.validated_data.get('corrections', {})
            
            with connection.cursor() as cursor:
                if is_confirmed:
                    # 정보 확인 완료 - 상태를 completed로 변경
                    cursor.execute("""
                        UPDATE receipt_info 
                        SET status = 'completed', updated_at = NOW()
                        WHERE receipt_id = %s AND user_id = %s
                    """, [receipt_id, request.user_id])
                    
                    return Response({
                        'success': True,
                        'message': '영수증 업로드가 완료되었습니다'
                    })
                else:
                    # 정보 수정 필요
                    return Response({
                        'success': False,
                        'message': '정보 확인이 필요합니다'
                    }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"영수증 확인 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '영수증 확인 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReceiptListView(APIView):
    """
    사용자 영수증 목록 조회 API
    """
    @admin_required
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT receipt_id, store_name, payment_date, amount, currency, status, created_at
                    FROM receipt_info 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC
                """, [request.user_id])
                
                columns = [col[0] for col in cursor.description]
                receipts = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                serializer = ReceiptListSerializer(receipts, many=True)
                return Response({
                    'success': True,
                    'data': serializer.data
                })

        except Exception as e:
            logger.error(f"영수증 목록 조회 오류: {str(e)}")
            return Response({
                'success': False,
                'message': '영수증 목록 조회 중 오류 발생'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)