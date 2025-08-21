from django.urls import path
from .views import (
    UserManagementView,
    ConversationReportView,
    ReceiptManagementView,
    ReceiptPreviewView
)

urlpatterns = [
    path('users/', UserManagementView.as_view(), name='admin-users'),
    path('conversations/reports/', ConversationReportView.as_view(), name='admin-reports'),
    path('receipts/', ReceiptManagementView.as_view(), name='admin-receipts'),
    path('receipts/list/', ReceiptManagementView.as_view(), name='admin-receipts-list'),
    path('receipts/<str:receipt_id>/preview/', ReceiptPreviewView.as_view(), name='receipt-preview'),
]
