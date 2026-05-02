from django.contrib import admin
from django.utils.html import format_html
import requests

from .models import Product

_user_cache: dict[int, dict] = {}


def _get_user(vendor_id: int) -> dict | None:
    if vendor_id in _user_cache:
        return _user_cache[vendor_id]

    # Try docker service name first, then localhost.
    for base in ("http://users:8000", "http://127.0.0.1:8000", "http://localhost:8000"):
        try:
            r = requests.get(f"{base}/api/public-users/", params={"ids": str(vendor_id)}, timeout=2)
            if r.status_code != 200:
                continue
            data = r.json()
            if isinstance(data, list) and data:
                _user_cache[vendor_id] = data[0]
                return data[0]
        except requests.RequestException:
            continue

    _user_cache[vendor_id] = None
    return None


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "stock",
        "vendor_id",
        "vendor_username",
        "image_preview",
    )
    list_filter = ("category",)
    search_fields = ("name", "description")

    def vendor_username(self, obj: Product):
        info = _get_user(int(obj.vendor_id))
        return (info or {}).get("username") or "-"

    vendor_username.short_description = "Vendor"

    def image_preview(self, obj: Product):
        if not obj.image:
            return "-"
        try:
            return format_html('<img src="{}" style="height:40px; width:auto;" />', obj.image.url)
        except Exception:
            return "-"

    image_preview.short_description = "Image"
