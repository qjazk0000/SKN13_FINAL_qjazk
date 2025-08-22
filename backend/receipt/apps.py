# receipt/apps.py
from django.apps import AppConfig

class ReceiptConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'receipt'
    verbose_name = '영수증 관리'