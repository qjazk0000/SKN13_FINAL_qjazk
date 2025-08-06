from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('chat/history/', views.chat_history, name='chat_history'),
    path('chat/create/', views.create_chat, name='create_chat'),
    path('chat/<str:session_id>/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/<str:session_id>/title/', views.update_chat_title, name='update_chat_title'),
    path('chat/<str:session_id>/delete/', views.delete_chat, name='delete_chat'),
]
