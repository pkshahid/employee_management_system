from django.urls import path,include
from .api_views import RegisterView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api_register'),
]