from django.urls import path
from .views import (
    api_add_product_view,
    api_my_products_view,
    api_product_detail_view,
    api_products_view,
)

urlpatterns = [
    path('', api_products_view),
    path('create/', api_add_product_view),
    path('vendor/', api_my_products_view),
    path('<int:pk>/', api_product_detail_view),
]
