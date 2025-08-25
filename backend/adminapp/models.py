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

class FileInfo(models.Model):
    file_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    # 문제가 되는 ForeignKey 관계 주석 처리
    # chat = models.ForeignKey(
    #     'chatbot.ChatHistory',  # chatbot 앱의 ChatHistory 참조
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     db_column='chat_id'
    # )
    chat_id = models.UUIDField(null=True, blank=True, db_column='chat_id')  # 임시로 UUIDField로 변경
    
#     file_origin_name = models.CharField(max_length=100)
#     file_name = models.CharField(max_length=100)
#     file_path = models.CharField(max_length=500)
#     file_size = models.BigIntegerField()
#     file_ext = models.CharField(max_length=10, null=True, blank=True)
#     uploaded_at = models.DateTimeField(default=timezone.now)
    
#     # 시리얼라이저에서 사용하는 필드들 추가
#     is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'file_info'
        verbose_name = '파일 정보'
        verbose_name_plural = '파일 정보 목록'

class Receipt(models.Model):
    """
    영수증 정보 모델 (receipt_info 테이블과 매핑)
    """
    RECEIPT_STATUS_CHOICES = [
        ('pending', '대기'),
        ('processing', '처리중'),
        ('completed', '완료'),
        ('failed', '실패')
    ]

    receipt_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    file_id = models.UUIDField()  # file_info 테이블 참조
    user_id = models.UUIDField()  # user_info 테이블 참조
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
        verbose_name = '영수증 정보'
        verbose_name_plural = '영수증 정보 목록'
        indexes = [
            models.Index(fields=['user_id'], name='idx_receipt_user'),
            models.Index(fields=['status'], name='idx_receipt_status'),
            models.Index(fields=['created_at'], name='idx_receipt_created'),
        ]

    def __str__(self):
        return f"Receipt {self.receipt_id} - {self.amount} {self.currency}"