# authapp/urls.py

from django.urls import path
from .views import (
    login_view,
    logout_view,
    password_change_view,
    auto_login_view,
    auth_status_view,
    user_profile_view,
)

urlpatterns = [
    path('login/', login_view),
    path('logout/', logout_view),
    path('user/password-change/', password_change_view),
    path('auto-login/', auto_login_view),
    path('auth/status/', auth_status_view),
    path('user/profile/', user_profile_view),
]
