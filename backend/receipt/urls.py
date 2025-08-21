#receipt/urls.py

from django.urls import path
from .views import (
    FileUploadView,
    ReceiptExtractionView,
    ReceiptConfirmationView,
    ReceiptListView
)

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='receipt-upload'),
    path('list/', ReceiptListView.as_view(), name='receipt-list'),
    path('<uuid:receipt_id>/extraction/', ReceiptExtractionView.as_view(), name='receipt-extraction'),
    path('<uuid:receipt_id>/confirm/', ReceiptConfirmationView.as_view(), name='receipt-confirm'),
]
