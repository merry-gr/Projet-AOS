from django.contrib import admin
import requests

from .models import Order, OrderItem

_users_cache: dict[int, dict] = {}
_products_cache: dict[int, dict] = {}


def _get_public_user(user_id: int) -> dict | None:
    if user_id in _users_cache:
        return _users_cache[user_id]

    for base in ("http://users:8000", "http://127.0.0.1:8000", "http://localhost:8000"):
        try:
            r = requests.get(f"{base}/api/public-users/", params={"ids": str(user_id)}, timeout=2)
            if r.status_code != 200:
                continue
            data = r.json()
            if isinstance(data, list) and data:
                _users_cache[user_id] = data[0]
                return data[0]
        except requests.RequestException:
            continue

    _users_cache[user_id] = None
    return None


def _get_product(product_id: int) -> dict | None:
    if product_id in _products_cache:
        return _products_cache[product_id]

    for base in ("http://products:8000", "http://127.0.0.1:8001", "http://localhost:8001"):
        try:
            r = requests.get(f"{base}/api/products/{product_id}/", timeout=2)
            if r.status_code != 200:
                continue
            data = r.json()
            if isinstance(data, dict) and data.get("id") == product_id:
                _products_cache[product_id] = data
                return data
        except requests.RequestException:
            continue

    _products_cache[product_id] = None
    return None


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "vendor_id", "vendor_username")
    fields = ("product_id", "product_name", "quantity", "vendor_id", "vendor_username")

    def product_name(self, obj: OrderItem):
        info = _get_product(int(obj.product_id))
        return (info or {}).get("name") or "-"

    def vendor_id(self, obj: OrderItem):
        info = _get_product(int(obj.product_id)) or {}
        return info.get("vendor_id") or "-"

    def vendor_username(self, obj: OrderItem):
        info = _get_product(int(obj.product_id)) or {}
        vid = info.get("vendor_id")
        if not vid:
            return "-"
        u = _get_public_user(int(vid)) or {}
        return u.get("username") or "-"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer_id", "buyer_username", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("id", "buyer_id", "phone", "city")
    inlines = [OrderItemInline]

    def buyer_username(self, obj: Order):
        u = _get_public_user(int(obj.buyer_id)) or {}
        return u.get("username") or "-"

    buyer_username.short_description = "Buyer"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order_id", "product_id", "product_name", "quantity")
    search_fields = ("order_id", "product_id")

    def product_name(self, obj: OrderItem):
        info = _get_product(int(obj.product_id))
        return (info or {}).get("name") or "-"