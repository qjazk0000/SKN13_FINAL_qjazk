# receipt/views.py
class ReceiptExtractionView(APIView):
    """
    영수증 텍스트 추출 결과 확인 API
    - 사용자가 업로드 후 추출된 정보 확인
    """
    @require_auth
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
    @require_auth
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
