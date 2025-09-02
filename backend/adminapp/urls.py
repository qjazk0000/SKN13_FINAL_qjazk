# adminapp/urls.py
from django.urls import path
from .views import (
    AdminUsersView,
    ConversationReportView,
    ReceiptPreviewView,
    AdminReceiptDetailView,
    AdminReceiptsView,
    AdminReceiptsDownloadView,
    ChatReportFeedbackView,
    UpdateUseYnView
)

urlpatterns = [
    path('users/', AdminUsersView.as_view(), name='admin-users'),
    path('users/update_use_yn/', UpdateUseYnView.as_view(), name='admin-use-yn'),
    path('conversations/reports/', ConversationReportView.as_view(), name='admin-reports'),
    path('chat-reports/<uuid:chat_id>/feedback/', ChatReportFeedbackView.as_view(), name='admin-chat-feedback'),
    path('receipts/', AdminReceiptsView.as_view(), name='admin-receipts'),
    path('receipts/<uuid:receipt_id>/', AdminReceiptDetailView.as_view(), name='admin-receipt-detail'),
    path('receipts/<uuid:receipt_id>/preview/', ReceiptPreviewView.as_view(), name='receipt-preview'),
    path('receipts/download', AdminReceiptsDownloadView.as_view(), name='admin-receipts-download'),
]