# adminapp/urls.py

from django.urls import path
from .views import AdminUsersView

urlpatterns = [
    path('users/', AdminUsersView.as_view(), name='admin-users'),
]
