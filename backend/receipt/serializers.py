# receipt/serializers.py

from rest_framework import serializers
from .models import FileInfo, ReceiptInfo

class FileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileInfo
        fields = '__all__'
        read_only_fields = ('file_id','uploaded_at')

class ReceiptInfoSerializer(serializers.ModelSerializer):
    file = FileInfoSerializer(read_only=True)

    class Meta:
        model = ReceiptInfo
        fields = '__all__'
        read_only_fields = ('receipt_id','created_at','updated_at','status','extracted_text')
