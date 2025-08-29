# adminapp/urls.py
from django.urls import path
from .views import (
    AdminUsersView,
    AdminReceiptsView,
    UserManagementView,
    ConversationReportView,
    ReceiptManagementView,
    ReceiptPreviewView,
    AdminReceiptDetailView,
    AdminReceiptsView
)

urlpatterns = [
    path('users/', AdminUsersView.as_view(), name='admin-users'),
    path('conversations/reports/', ConversationReportView.as_view(), name='admin-reports'),
    path('receipts/', AdminReceiptsView.as_view(), name='admin-receipts'),
    path('receipts/<uuid:receipt_id>/', AdminReceiptDetailView.as_view(), name='admin-receipt-detail'),
    path('receipts/<uuid:receipt_id>/preview/', ReceiptPreviewView.as_view(), name='receipt-preview'),
]