from django.contrib import admin
from .models import RecJob, RecResultSummary, RecResultItem

@admin.register(RecJob)
class RecJobAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'user_id', 'status', 'original_filename', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('job_id', 'user_id', 'original_filename')
    readonly_fields = ('job_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('job_id', 'user_id', 'file_id', 'original_filename', 'model_version')
        }),
        ('S3 정보', {
            'fields': ('input_s3_key', 'result_s3_key')
        }),
        ('상태 정보', {
            'fields': ('status', 'error_message')
        }),
        ('시간 정보', {
            'fields': ('started_at', 'processed_at', 'created_at', 'updated_at')
        }),
    )

@admin.register(RecResultSummary)
class RecResultSummaryAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'store_name', 'payment_date', 'total_amount', 'currency', 'created_at')
    list_filter = ('currency', 'created_at')
    search_fields = ('job_id', 'store_name', 'card_company')
    readonly_fields = ('job_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(RecResultItem)
class RecResultItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'job_id', 'name', 'unit_price', 'quantity', 'amount', 'line_no')
    list_filter = ('line_no', 'created_at')
    search_fields = ('name', 'job_id')
    readonly_fields = ('item_id', 'created_at')
    ordering = ('job_id', 'line_no')
