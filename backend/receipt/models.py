# receipt/models.py
from django.db import models
import uuid

class FileInfo(models.Model):
    """
    파일 업로드 정보 테이블
    """
    file_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    chat = models.ForeignKey(
        'chatbot.ChatHistory',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='chat_id'
    )
    file_origin_name = models.CharField(max_length=100)
    file_name = models.CharField(max_length=100)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    file_ext = models.CharField(max_length=10, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'file_info'
        verbose_name = '파일 정보'
        verbose_name_plural = '파일 정보 목록'

class ReceiptInfo(models.Model):
    """
    영수증 정보 테이블
    """
    STATUS_CHOICES = [
        ('pending', '처리 대기'),
        ('processing', '처리 중'),
        ('completed', '처리 완료'),
        ('failed', '처리 실패')
    ]

    receipt_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    file = models.ForeignKey(
        FileInfo,
        on_delete=models.CASCADE,
        db_column='file_id'
    )
    user = models.ForeignKey(
        'authapp.User',
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    payment_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='KRW')
    store_name = models.CharField(max_length=200, null=True, blank=True)
    extracted_text = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'receipt_info'
        verbose_name = '영수증 정보'
        verbose_name_plural = '영수증 정보 목록'
        indexes = [
            models.Index(fields=['user'], name='idx_receipt_user'),
            models.Index(fields=['payment_date'], name='idx_receipt_date'),
            models.Index(fields=['status'], name='idx_receipt_status'),
        ]