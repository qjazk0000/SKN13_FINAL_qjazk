from django.urls import path
from django.http import JsonResponse
from . import views

app_name = 'chatbot'

def api_root(request):
    """API 루트 엔드포인트"""
    return JsonResponse({
        "message": "Chatbot API",
        "endpoints": {
            "chat_history": "/api/chat/history/",
            "create_chat": "/api/chat/create/",
            "send_message": "/api/chat/send/",
            "get_messages": "/api/chat/{session_id}/messages/",
            "update_title": "/api/chat/{session_id}/title/",
            "delete_chat": "/api/chat/{session_id}/delete/"
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),  # API 루트 추가
    path('chat/history/', views.chat_history, name='chat_history'),
    path('chat/create/', views.create_chat, name='create_chat'),
    path('chat/<str:session_id>/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/<str:session_id>/title/', views.update_chat_title, name='update_chat_title'),
    path('chat/<str:session_id>/delete/', views.delete_chat, name='delete_chat'),
]
