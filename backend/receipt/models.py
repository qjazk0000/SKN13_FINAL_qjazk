# receipt/models.py
from django.db import models
import uuid

# class FileInfo(models.Model):
#     """
#     파일 업로드 정보 테이블 - DB에 이미 존재하는 테이블 매핑용
#     """
#     file_id = models.UUIDField(primary_key=True)
#     chat_id = models.UUIDField(null=True, blank=True)
#     file_origin_name = models.CharField(max_length=100)
#     file_name = models.CharField(max_length=100)
#     file_path = models.CharField(max_length=500)
#     file_size = models.BigIntegerField()
#     file_ext = models.CharField(max_length=10, null=True, blank=True)
#     uploaded_at = models.DateTimeField()

#     class Meta:
#         db_table = 'file_info'
#         managed = False  # Django가 테이블 생성/수정하지 않음
#         verbose_name = '파일 정보'
#         verbose_name_plural = '파일 정보 목록'

#     def __str__(self):
#         return self.file_origin_name
    
class ReceiptInfo(models.Model):
    """
    영수증 정보 테이블
    """
    receipt_id = models.UUIDField(primary_key=True)
    file_id = models.UUIDField()
    user_id = models.UUIDField()  # ✅ ForeignKey 아님
    payment_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='KRW')
    store_name = models.CharField(max_length=200, null=True, blank=True)
    extracted_text = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'receipt_info'
        managed = False
        verbose_name = '영수증 정보'
        verbose_name_plural = '영수증 정보 목록'
        
    def __str__(self):
        return f"{self.store_name} - {self.amount}"