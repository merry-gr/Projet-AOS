from django.urls import path
from .views import create_order_api, order_detail_api, orders_api

urlpatterns = [
    path('', orders_api),
    path('create/', create_order_api),
    path('<int:pk>/', order_detail_api),
   
]
