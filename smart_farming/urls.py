from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from user_app.views import custom_login

urlpatterns = [
    path('admin/', admin.site.urls),
    # Map the common login URL used by the frontend
    path('accounts/login/', custom_login, name='login'),
    # Logout handled by standard Django view (next_page='/')
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    # Include all other app-level URLs
    path('', include('user_app.urls')),
]
