#receipt/urls.py

from django.urls import path
from .views import FileUploadView, ReceiptListView, ReceiptDetailView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='receipt-upload'),
    path('', ReceiptListView.as_view(), name='receipt-list'),
    path('<uuid:receipt_id>/', ReceiptDetailView.as_view(), name='receipt-detail'),
]
