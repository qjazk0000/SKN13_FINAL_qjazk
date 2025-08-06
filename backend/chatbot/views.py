from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import time
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer

# 임시 메모리 저장소 (개발용)
chat_sessions = {}
current_chat_id = None

@api_view(['GET'])
def chat_history(request):
    """채팅 세션 목록 조회"""
    sessions = ChatSession.objects.all()
    serializer = ChatSessionSerializer(sessions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_chat(request):
    """새 채팅 세션 생성"""
    session_id = f"{int(time.time() * 1000)}"
    session = ChatSession.objects.create(
        session_id=session_id,
        title="새로운 대화"
    )
    serializer = ChatSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_chat_messages(request, session_id):
    """특정 채팅 세션의 메시지 조회"""
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = session.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def send_message(request):
    """메시지 전송 및 AI 응답"""
    data = request.data
    session_id = data.get('session_id')
    message_content = data.get('message')
    message_type = data.get('type', 'text')
    
    try:
        session = ChatSession.objects.get(session_id=session_id)
        
        # 사용자 메시지 저장
        user_message = ChatMessage.objects.create(
            session=session,
            sender='user',
            content=message_content,
            message_type=message_type
        )
        
        # AI 응답 생성 (더미)
        ai_response = f"AI 응답: {message_content}"
        ai_message = ChatMessage.objects.create(
            session=session,
            sender='ai',
            content=ai_response,
            message_type='text'
        )
        
        # 세션 제목 업데이트 (첫 번째 메시지인 경우)
        if session.messages.count() == 2:  # 사용자 메시지 + AI 응답
            session.title = message_content[:50]
            session.save()
        
        return Response({
            'user_message': ChatMessageSerializer(user_message).data,
            'ai_message': ChatMessageSerializer(ai_message).data
        })
        
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def update_chat_title(request, session_id):
    """채팅 세션 제목 업데이트"""
    try:
        session = ChatSession.objects.get(session_id=session_id)
        session.title = request.data.get('title', session.title)
        session.save()
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_chat(request, session_id):
    """채팅 세션 삭제"""
    try:
        session = ChatSession.objects.get(session_id=session_id)
        session.delete()
        return Response({'message': 'Chat session deleted'})
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
