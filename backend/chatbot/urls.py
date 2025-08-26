# chatbot/urls.py
from django.urls import path
from .views import (
    ConversationListView,
    ConversationCreateView,
    ConversationDeleteView,
    ChatQueryView,
    ChatStatusView,
)

urlpatterns = [
    path('list/', ConversationListView.as_view(), name='conversation-list'),
    path('new/', ConversationCreateView.as_view(), name='conversation-create'),
    path('<uuid:conversation_id>/delete/', ConversationDeleteView.as_view(), name='conversation-delete'),
    path('<uuid:conversation_id>/query/', ChatQueryView.as_view(), name='chat-query'),
    path('<uuid:conversation_id>/status/', ChatStatusView.as_view(), name='chat-status'),
]