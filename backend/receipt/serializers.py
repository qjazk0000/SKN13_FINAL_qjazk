from rest_framework import serializers
import logging
# 11  
logger = logging.getLogger(__name__)

class ReceiptUploadSerializer(serializers.Serializer):
    files = serializers.FileField(
        required=True,
        # child=serializers.FileField(),
        # allow_empty=False,
        error_messages={
            'required': '업로드할 파일을 선택해주세요.',
            'blank': '업로드할 파일을 선택해주세요.'
        }
    )

from rest_framework import serializers

class ReceiptSaveSerializer(serializers.Serializer):
    receipts = serializers.ListField(
        child=serializers.DictField(),
        required=True
    )
    # store_name = serializers.CharField(required=False, allow_blank=True)
    # payment_date = serializers.CharField()  # 문자열로 받아서 View에서 normalize_date() 처리
    # amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    # card_info = serializers.CharField(required=False, allow_blank=True)
    # items = serializers.ListField(required=False)

    def validate(self, data):
        """
        OCR이 제공한 값이 모두 비어 있으면 저장할 수 없도록 처리
        """
        if not data.get('receipts'):
            raise serializers.ValidationError("저장할 영수증 정보가 없습니다.")
        return data

class ReceiptDownloadSerializer(serializers.Serializer):
    start_date = serializers.CharField(
        error_messages={'required': '시작일을 입력해주세요.'}
    )
    end_date = serializers.CharField(
        error_messages={'required': '종료일을 입력해주세요.'}
    )