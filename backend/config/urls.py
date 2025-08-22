# config/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from authapp.views import PasswordChangeView

# API 엔드포인트 정의
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', include('chatbot.urls')),
    path('api/qdrant/', include('qdrant.urls')),
    path('api/auth/', include('authapp.urls')),
    path('api/receipt/', include('receipt.urls')),
    path('api/admin/', include('adminapp.urls')),  # 관리자용 API
    path('api/user/password-change/', PasswordChangeView.as_view(), name='user-password-change'),
]

# DEBUG 모드에서 정적 파일과 미디어 파일을 서빙 (admin 페이지를 위함)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
