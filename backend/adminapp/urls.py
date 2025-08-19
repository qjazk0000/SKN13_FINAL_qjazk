# adminapp/urls.py

from django.urls import path
from .views import AdminUsersView, AdminReceiptsView

urlpatterns = [
    path('users/', AdminUsersView.as_view(), name='admin-users'),
    path('receipts/list/', AdminReceiptsView.as_view(), name='admin-receipts'),
]
