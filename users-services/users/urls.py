from django.urls import path
from .views import (
    login_api,
    register_api,
    profile_api,
    public_users_api,
    admin_users_api,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', register_api),
    path('login/', login_api),
    path('refresh/', TokenRefreshView.as_view()),
    # legacy user listing endpoints removed; keep minimal API surface used by front-end
    path('profile/', profile_api),
    path('public-users/', public_users_api),
    path('admin/users/', admin_users_api),
]