# authapp/urls.py

from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    UserProfileView,
    # PasswordChangeView,  # 메인 URL에서 직접 처리
    # password_change_view,
    # auto_login_view,
    # auth_status_view,
    # user_profile_view,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('user/password-change/', password_change_view),
    # path('auto-login/', auto_login_view),
    # path('auth/status/', auth_status_view),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    # path('password-change/', PasswordChangeView.as_view(), name='password-change'),  # 메인 URL에서 처리
]
