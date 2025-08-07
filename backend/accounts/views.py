from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
import json


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