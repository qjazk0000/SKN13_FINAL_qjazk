# authapp/urls.py

from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    RefreshTokenView,
    UserProfileView,
    PasswordChangeView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password-change/', PasswordChangeView.as_view(), name='password-change'),
]