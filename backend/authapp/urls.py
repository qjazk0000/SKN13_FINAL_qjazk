# authapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password-change/', password_change_view, name='password-change'), 
    
]