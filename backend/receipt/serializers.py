# receipt/serializers.py

from rest_framework import serializers
from .models import RecJob, RecResultSummary, RecResultItem

class RecJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecJob
        fields = '__all__'
        read_only_fields = ('job_id', 'created_at', 'updated_at')

class RecJobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecJob
        fields = ('original_filename', 'model_version')

class RecJobDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecJob
        fields = ('job_id', 'status', 'original_filename', 'created_at', 'updated_at', 'error_message')

class RecJobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecJob
        fields = ('job_id', 'status', 'original_filename', 'created_at', 'updated_at')

class RecResultSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecResultSummary
        fields = '__all__'
        read_only_fields = ('job_id', 'created_at', 'updated_at')

class RecResultItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecResultItem
        fields = '__all__'
        read_only_fields = ('item_id', 'created_at')
