#receipt/urls.py  

from django.urls import path
from .views import ReceiptUploadView, ReceiptSaveView, ReceiptDownloadView, ReceiptDetailView

urlpatterns = [
    path('upload/', ReceiptUploadView.as_view()),
    path('modify/', ReceiptDetailView.as_view()),
    path('save/', ReceiptSaveView.as_view()),
    path('download/', ReceiptDownloadView.as_view()),
    path('<str:receipt_id>/', ReceiptDetailView.as_view()),
]
