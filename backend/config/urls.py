from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from authapp import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chatbot.urls')),
    path('auth/', include('receipt.urls')),
    path('login/', auth_views.login_view),
    path('logout/', auth_views.logout_view),
    path('user/password-change/', auth_views.password_change_view),
    path('auto-login/', auth_views.auto_login_view),
    path('auth/status/', auth_views.auth_status_view),    
    path('user/profile', auth_views.user_profile_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
