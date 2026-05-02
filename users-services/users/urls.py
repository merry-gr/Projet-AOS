from django.urls import path
from .views import api_public_users_view, api_users_view, login_api, register_api
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', register_api),
    path('login/', login_api),
    
    path('refresh/', TokenRefreshView.as_view()),
    path('users/', api_users_view),
    path('public-users/', api_public_users_view),
]