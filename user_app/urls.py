from django.urls import path
from .views import (home, crop_recommendation, fertilizer_recommendation, disease_detection, 
                    logout_view, register, admin_dashboard, create_admin, change_password_admin)
from .chatbot_views import chatbot_api

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('crop/', crop_recommendation, name='crop'),
    path('fertilizer/', fertilizer_recommendation, name='fertilizer'),
    path('disease/', disease_detection, name='disease'),
    path('logout/', logout_view, name='logout'),
    path('management/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('management/create-admin/', create_admin, name='create_admin'),
    path('management/change-password/', change_password_admin, name='change_password_admin'),
    path('chatbot/', chatbot_api, name='chatbot_api'),
]
