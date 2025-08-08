from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

# API 엔드포인트 정의
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/accounts/', include('accounts.urls')),
]

# DEBUG 모드에서 정적 파일과 미디어 파일을 서빙 (admin 페이지를 위함)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
