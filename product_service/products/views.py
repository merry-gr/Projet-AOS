import base64
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer


def get_user_id_from_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None

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


@api_view(['GET'])
def api_products_view(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def api_add_product_view(request):
    data = request.data.copy()
    if not data.get('vendor_id'):
        vendor_id = get_user_id_from_token(request)
        if vendor_id:
            data['vendor_id'] = vendor_id

    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        product = serializer.save()
        return Response({"message": "Product created", "id": product.id}, status=201)

    return Response(serializer.errors, status=400)


@api_view(['GET'])
def api_my_products_view(request):
    vendor_id = request.GET.get('vendor_id') or get_user_id_from_token(request)
    if not vendor_id:
        return Response({"error": "vendor_id is required"}, status=400)

    products = Product.objects.filter(vendor_id=vendor_id)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PATCH', 'DELETE'])
def api_product_detail_view(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    if request.method == 'DELETE':
        vendor_id = request.GET.get('vendor_id') or get_user_id_from_token(request)
        if vendor_id and str(product.vendor_id) != str(vendor_id):
            return Response({"error": "You can only delete your own products"}, status=403)

        product.delete()
        return Response({"message": "Product deleted"})

    if request.method == 'PATCH':
        vendor_id = request.GET.get('vendor_id') or get_user_id_from_token(request)
        if vendor_id and str(product.vendor_id) != str(vendor_id):
            return Response({"error": "You can only edit your own products"}, status=403)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    serializer = ProductSerializer(product)
    return Response(serializer.data)
