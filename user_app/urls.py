from django.urls import path
from . import views
from .chatbot_views import chatbot_api

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('crop/', views.crop_recommendation, name='crop'),
    path('fertilizer/', views.fertilizer_recommendation, name='fertilizer'),
    path('disease/', views.disease_detection, name='disease'),
    path('management/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('management/create-admin/', views.create_admin, name='create_admin'),
    path('management/change-password/', views.change_password_admin, name='change_password_admin'),
    path('chatbot/', chatbot_api, name='chatbot_api'),
    path('api/weather/', views.get_weather, name='get_weather'),
]
