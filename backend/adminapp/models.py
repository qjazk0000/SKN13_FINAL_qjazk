# adminapp/models.py
from django.db import models
from django.utils import timezone
import uuid

class AdminUser(models.Model):
    admin_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    admin_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'admin_user'
        verbose_name = '관리자'
        verbose_name_plural = '관리자 목록'

class ReportedConversation(models.Model):
    REPORT_STATUS_CHOICES = [
        ('pending', '대기'),
        ('completed', '처리 완료'),
        ('rejected', '거부됨')
    ]

    report_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    chat_id = models.UUIDField()
    user_id = models.UUIDField()
    session_id = models.UUIDField()
    report_reason = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=REPORT_STATUS_CHOICES,
        default='pending'
    )

    class Meta:
        db_table = 'reported_conversation'
        verbose_name = '신고된 대화'
        verbose_name_plural = '신고된 대화 목록'
        indexes = [
            models.Index(fields=['chat_id'], name='idx_reported_chat'),
            models.Index(fields=['user_id'], name='idx_reported_user'),
            models.Index(fields=['session_id'], name='idx_reported_session'),
        ]

class Receipt(models.Model):
    RECEIPT_STATUS_CHOICES = [
        ('pending', '검증 대기'),
        ('verified', '검증 완료'),
        ('rejected', '거부됨')
    ]

    receipt_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    file = models.ForeignKey(
        'FileInfo',
        on_delete=models.CASCADE,
        db_column='file_id'
    )
    user = models.ForeignKey(
        'authapp.User',  # authapp의 User 모델 참조
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
        choices=RECEIPT_STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'receipt_info'
        verbose_name = '영수증'
        verbose_name_plural = '영수증 목록'
        indexes = [
            models.Index(fields=['user'], name='idx_receipt_user'),
            models.Index(fields=['payment_date'], name='idx_receipt_date'),
        ]

class FileInfo(models.Model):
    file_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    chat = models.ForeignKey(
        'chatbot.ChatHistory',  # chatbot 앱의 ChatHistory 참조
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
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'file_info'
        verbose_name = '파일 정보'
        verbose_name_plural = '파일 정보 목록'