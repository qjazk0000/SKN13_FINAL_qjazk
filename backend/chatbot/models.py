import uuid
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Conversation(models.Model):
    """
    대화방 모델
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="대화 ID"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name="사용자"
    )
    title = models.CharField(
        max_length=200,
        default="새로운 대화",
        verbose_name="제목"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시"
    )

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "대화방"
        verbose_name_plural = "대화방 목록"

    def __str__(self):
        return f"[{self.user.username}] {self.title} ({self.id})"

class ChatMessage(models.Model):
    """
    채팅 메시지 모델
    """
    SENDER_CHOICES = [
        ('user', '사용자'),
        ('ai', 'AI'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="메시지 ID"
    )
    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE,
        verbose_name="대화방"
    )
    sender_type = models.CharField(
        max_length=10,
        choices=SENDER_CHOICES,
        verbose_name="발신자 유형"
    )
    content = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = "채팅 메시지"
        verbose_name_plural = "채팅 메시지 목록"

    def __str__(self):
        return f"{self.get_sender_type_display()}: {self.content[:50]}"

# class FileInfo(models.Model):
#     file_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     chat = models.ForeignKey(ChatMessage, null=True, blank=True, on_delete=models.SET_NULL)
#     file_origin_name = models.CharField(max_length=512)
#     file = models.FileField(upload_to='uploads/receipts/%Y/%m/%d/')
#     file_size = models.BigIntegerField()
#     file_ext = models.CharField(max_length=32, null=True, blank=True)
#     uploaded_at = models.DateTimeField(auto_now_add=True)

# class ReceiptInfo(models.Model):
#     STATUS_CHOICES = (
#         ('pending','pending'),
#         ('processing','processing'),
#         ('processed','processed'),
#         ('failed','failed')
#     )
#     receipt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     file = models.ForeignKey(FileInfo, on_delete=models.CASCADE)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     payment_date = models.DateTimeField(null=True, blank=True)
#     amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
#     currency = models.CharField(max_length=10, default='KRW', null=True, blank=True)
#     store_name = models.CharField(max_length=255, null=True, blank=True)
#     extracted_text = models.TextField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)