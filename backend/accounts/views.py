from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
import json
from django.contrib.auth import authenticate, login, logout, get_user, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password

@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_login_id = data.get("user_login_id")
            password = data.get("password")

            if not user_login_id or not password:
                return JsonResponse({"error": "아이디와 비밀번호를 입력하세요"}, status=400)
            
            user = authenticate(username=user_login_id, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    "token": str(refresh.access_token),
                    "regresh": str(refresh),
                    "user": user.username
                }, status=200)
            else:
                return JsonResponse({"error": "아이디 또는 비밀번호가 잘못되었습니다."}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)
    return JsonResponse({"error": "허용되지 않은 메서드입니다."}, status=405)

@csrf_exempt
@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': '로그아웃 성공'}, status=200)
    return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)


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

            if not check_password(current_password, user.password):
                return JsonResponse({"error": "현재 비밀번호가 일치하지 않습니다."}, status=401)

            if new_password != confirm_password:
                return JsonResponse({"error": "새 비밀번호가 서로 일치하지 않습니다."}, status=400)

            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)

            return JsonResponse({"message": "비밀번호가 성공적으로 변경되었습니다."}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON 파싱 실패"}, status=400)

    return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)


@csrf_exempt
@login_required
def auto_login_view(request):
    if request.method == 'POST':
        return JsonResponse({'message': '자동 로그인 성공'}, status=200)
    return JsonResponse({'error': 'POST 요청만 허용됩니다'}, status=405)


@csrf_exempt
def auth_status_view(request):
    user = get_user(request)
    if user.is_authenticated:
        return JsonResponse({'status': 'authenticated', 'user': user.username}, status=200)
    else:
        return JsonResponse({'status': 'unauthenticated'}, status=401)


@login_required
def user_profile_view(request):
    user = request.user
    return JsonResponse({
        "이름": user.username,
        "메일": user.email,
        "부서": getattr(user, 'dept', 'N/A'),
        "직급": getattr(user, 'rank', 'N/A')
    }, status=200)