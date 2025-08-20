# receipt/serializers.py
from rest_framework import serializers
from .models import FileInfo, ReceiptInfo

class FileUploadSerializer(serializers.Serializer):
    """
    파일 업로드 요청 데이터 검증 시리얼라이저
    """
    file = serializers.FileField(
        max_length=100,
        help_text="업로드할 파일"
    )

# receipt/serializers.py
class ReceiptExtractionSerializer(serializers.ModelSerializer):
    """
    영수증 추출 정보 응답 시리얼라이저 (사용자 확인용)
    """
    file_name = serializers.CharField(source='file.file_origin_name', read_only=True)
    
    class Meta:
        model = ReceiptInfo
        fields = [
            'receipt_id',
            'file_name',        # 파일 이름
            'store_name',       # 가맹점명
            'payment_date',     # 결제일시
            'amount',           # 결제금액
            'currency',         # 통화
            'extracted_text'    # 추출된 텍스트
        ]
        read_only_fields = fields

class ReceiptConfirmSerializer(serializers.Serializer):
    """
    영수증 확인 및 업로드 요청 시리얼라이저
    """
    is_confirmed = serializers.BooleanField(
        required=True,
        help_text="추출 정보 확인 여부"
    )

class ReceiptDetailSerializer(serializers.ModelSerializer):
    """
    영수증 상세 정보 응답 시리얼라이저 (관리자 페이지)
    """

    class Meta:
        model = ReceiptInfo
        fields = [
            'receipt_id',
            'user_id',
            'payment_date',
            'amount',
            'currency',
            'store_name',
            'file_path',
            'extracted_text',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields

class ReceiptProcessSerializer(serializers.Serializer):
    """
    영수증 처리 상태 업데이트 시리얼라이저
    """
    status = serializers.ChoiceField(
        choices=ReceiptInfo.STATUS_CHOICES,
        help_text="처리 상태"
    )
    extracted_text = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="OCR로 추출된 텍스트"
    )