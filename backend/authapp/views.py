from django.shortcuts import render
# authapp/views.py

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_login_id = data.get('user_login_id')
            password = data.get('passwd')

            user = authenticate(request, username=user_login_id, password=passwd)

            if user is not None:
                login(request, user)  # Django 세션 로그인 처리
                return JsonResponse({'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Only POST allowed'}, status=405)

###########################################################################

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash

@csrf_exempt
@login_required
def password_change_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            current_password = data.get("current_password")
            new_password = data.get("new_password")
            confirm_password = data.get("confirm_password")

            user = request.user

            # 1. 현재 비밀번호 확인
            if not check_password(current_password, user.passwd):
                return JsonResponse({"error": "현재 비밀번호가 일치하지 않습니다."}, status=401)

            # 2. 새 비밀번호 일치 확인
            if new_password != confirm_password:
                return JsonResponse({"error": "새 비밀번호가 서로 일치하지 않습니다."}, status=400)

            # 3. 비밀번호 변경
            user.set_password(new_password)
            user.save()

            # 4. 세션 유지
            update_session_auth_hash(request, user)

            return JsonResponse({"message": "비밀번호가 성공적으로 변경되었습니다."}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON 파싱 실패"}, status=400)

    return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)

###########################################################################
# 로그아웃

from django.contrib.auth import logout
from django.utils.decorators import method_decorator

@csrf_exempt
@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)  # 세션 종료
        return JsonResponse({'message': '로그아웃 성공'}, status=200)
    
    return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)

#########################################################################
# 자동 로그인

@csrf_exempt
@login_required
def auto_login_view(request):
    if request.method == 'POST':
        return JsonResponse({'message': '자동 로그인 성공'}, status=200)
    return JsonResponse({'error': 'POST 요청만 허용됩니다'}, status=405)

##########################################################################
# 로그인 상태 확인

from django.contrib.auth import get_user

@csrf_exempt
def auth_status_view(request):
    user = get_user(request)
    if user.is_authenticated:
        return JsonResponse({'status': 'authenticated', 'user': user.username}, status=200)
    else:
        return JsonResponse({'status': 'unauthenticated'}, status=401)

##########################################################################
# 마이페이지

@login_required
def user_profile_view(request):
    user = request.user
    return JsonResponse({
        "이름": user.username,
        "메일": user.email,
        "부서": user.dept,
        "직급": user.rank
    }, status=200)