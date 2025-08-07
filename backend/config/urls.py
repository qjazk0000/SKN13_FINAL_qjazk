from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from .views import serve_react

from django.http import JsonResponse

def root_view(request):
    """루트 URL에 대한 응답"""
    return JsonResponse({
        "message": "SKN13-FINAL-6Team API Server",
        "status": "running",
        "endpoints": {
            "admin": "/admin/",
            "api": "/api/",
            "docs": "/api/docs/"
        }
    })

urlpatterns = [
    path('', root_view, name='root'),  # 루트 URL 추가
    path('admin/', admin.site.urls),
    path('api/', include('chatbot.urls')),
    path('api/accounts/', include('accounts.urls')),
    
    # React 앱을 루트 경로에서 서빙
    re_path(r'^(?!admin/|api/|static/|media/).*$', serve_react, name='react_app'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
