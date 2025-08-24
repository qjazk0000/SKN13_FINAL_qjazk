# receipt/models.py

import uuid
from django.db import models

class RecJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        QUEUED = "QUEUED" 
        RUNNING = "RUNNING"
        DONE = "DONE"
        FAILED = "FAILED"

    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()  # user_info 테이블의 user_id 참조
    file_id = models.UUIDField(null=True, blank=True)  # file_info 테이블 참조 (선택적)
    input_s3_key = models.CharField(max_length=500)
    result_s3_key = models.CharField(max_length=500, null=True, blank=True)
    original_filename = models.CharField(max_length=255, null=True, blank=True)
    model_version = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    queued_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"RecJob {self.job_id} - {self.status}"

    class Meta:
        db_table = 'rec_job'
        ordering = ['-created_at']


class RecResultSummary(models.Model):
    job_id = models.OneToOneField(RecJob, on_delete=models.CASCADE, primary_key=True, db_column='job_id')
    store_name = models.CharField(max_length=200, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    card_company = models.CharField(max_length=50, null=True, blank=True)
    card_number_masked = models.CharField(max_length=64, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='KRW')
    extracted_text = models.TextField(null=True, blank=True)
    raw_json = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RecResultSummary {self.job_id}"

    class Meta:
        db_table = 'rec_result_summary'


class RecResultItem(models.Model):
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_id = models.ForeignKey(RecJob, on_delete=models.CASCADE, db_column='job_id')
    name = models.CharField(max_length=300)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    line_no = models.IntegerField(null=True, blank=True)
    extra = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RecResultItem {self.item_id} - {self.name}"

    class Meta:
        db_table = 'rec_result_item'
        ordering = ['line_no']

