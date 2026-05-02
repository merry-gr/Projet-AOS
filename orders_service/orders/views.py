import base64
import json

import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderItem
from .serializers import OrderSerializer


def get_buyer_id(request):
    auth_header = request.headers.get('Authorization', '')

    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1]
        parts = token.split('.')
        if len(parts) < 2:
            return None

        try:
            payload = parts[1] + '=' * (-len(parts[1]) % 4)
            data = json.loads(base64.urlsafe_b64decode(payload))
            return data.get('user_id')
        except (ValueError, json.JSONDecodeError):
            return None

    return request.data.get('buyer_id')


def get_products():
    product_urls = getattr(settings, 'PRODUCT_SERVICE_URLS', [
        'http://products:8000/api/products/',
        'http://localhost:8001/api/products/',
    ])

    for url in product_urls:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            continue

    return None


def create_order(request):
    try:
        product_id = int(request.data.get('product_id'))
        quantity = int(request.data.get('quantity'))
    except (TypeError, ValueError):
        return Response({"error": "product_id and quantity are required numbers"}, status=400)

    buyer_id = get_buyer_id(request)
    if not buyer_id:
        return Response({"error": "buyer_id is required or provide a valid Bearer token"}, status=400)

    products = get_products()
    if products is None:
        return Response({"error": "Product service is unavailable"}, status=503)

    product = next((p for p in products if p['id'] == product_id), None)

    if not product:
        return Response({"error": "Product not found"}, status=404)

    if product['stock'] < quantity:
        return Response({"error": "Not enough stock"}, status=400)

    order = Order.objects.create(
        buyer_id=buyer_id,
        phone=request.data.get('phone', '000000'),
        delivery_address=request.data.get('delivery_address', 'test'),
        city=request.data.get('city', 'test'),
        delivery_note=request.data.get('delivery_note'),
        payment_method=request.data.get('payment_method', 'cash'),
    )

    OrderItem.objects.create(
        order=order,
        product_id=product_id,
        quantity=quantity,
    )

    return Response({
        "message": "Order created",
        "order_id": order.id,
        "buyer_id": order.buyer_id,
    }, status=201)


def list_orders():
    orders = Order.objects.all().prefetch_related('items')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


def update_order(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    status_value = request.data.get('status')
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if status_value not in valid_statuses:
        return Response({"error": "Invalid status"}, status=400)

    order.status = status_value
    order.estimated_delivery = request.data.get('estimated_delivery') or order.estimated_delivery
    order.vendor_note = request.data.get('vendor_note', order.vendor_note)
    order.save()

    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
def create_order_api(request):
    return create_order(request)


@api_view(['GET'])
def api_orders_view(request):
    return list_orders()


@api_view(['GET', 'POST'])
def orders_api(request):
    if request.method == 'POST':
        return create_order(request)

    return list_orders()


@api_view(['PATCH'])
def order_detail_api(request, pk):
    return update_order(request, pk)
