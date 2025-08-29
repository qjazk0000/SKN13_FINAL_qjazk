import uuid
from django.db import models
from django.conf import settings

class Conversation(models.Model):
    """
    대화방 모델
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="대화 ID",
        db_column='conversation_id'  # 실제 DB 컬럼명 매핑
    )
    user_id = models.CharField(
        max_length=100,
        verbose_name="사용자 ID"
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
        db_table = 'conversation_list'  # 실제 DB 테이블명 매핑

    def __str__(self):
        return f"[{self.user_id}] {self.title} ({self.id})"

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
        verbose_name="메시지 ID",
        db_column='chat_id'  # 실제 DB 컬럼명 매핑
    )
    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE,
        verbose_name="대화방",
        db_column='conversation_id'  # 실제 DB 컬럼명 매핑
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
        db_table = 'chat_history'  # 실제 DB 테이블명 매핑

    def __str__(self):
        return f"{self.get_sender_type_display()}: {self.content[:50]}"
    
    report = models.CharField(
        max_length=1,
        choices=[('N', '미신고'), ('Y', '신고')],
        default='N',
        verbose_name="신고 여부"
    )
