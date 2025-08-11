# receipt/models.py

import uuid
from django.db import models
from django.conf import settings

class FileInfo(models.Model):
    file_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_origin_name = models.CharField(max_length=512)
    file = models.FileField(upload_to='uploads/receipts/%Y/%m/%d/')
    file_size = models.BigIntegerField()
    file_ext = models.CharField(max_length=32, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_origin_name

class ReceiptInfo(models.Model):
    STATUS_CHOICES = (
        ('pending','pending'),
        ('processing','processing'),
        ('processed','processed'),
        ('failed','failed')
    )
    receipt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(FileInfo, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='KRW', null=True, blank=True)
    store_name = models.CharField(max_length=255, null=True, blank=True)
    extracted_text = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

