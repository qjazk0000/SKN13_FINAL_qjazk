# receipt/serializers.py
from rest_framework import serializers

class FileUploadSerializer(serializers.Serializer):
    """
    파일 업로드 요청 데이터 검증 시리얼라이저
    """
    file = serializers.FileField(
        max_length=100,
        help_text="업로드할 파일"
    )

class ReceiptExtractionSerializer(serializers.ModelSerializer):
    """
    영수증 추출 정보 응답 시리얼라이저 (사용자 확인용)
    """
    receipt_id = serializers.UUIDField()
    file_name = serializers.CharField()
    store_name = serializers.CharField()
    payment_date = serializers.DateTimeField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()
    extracted_text = serializers.CharField()

class ReceiptConfirmSerializer(serializers.Serializer):
    """
    영수증 확인 및 업로드 요청 시리얼라이저
    """
    is_confirmed = serializers.BooleanField(
        required=True,
        help_text="추출 정보 확인 여부"
    )

class ReceiptListSerializer(serializers.Serializer):
    """
    사용자 영수증 목록 응답 시리얼라이저
    """
    receipt_id = serializers.UUIDField()
    store_name = serializers.CharField()
    payment_date = serializers.DateTimeField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()