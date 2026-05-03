from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import BuyerProfile, User, VendorProfile


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("MedConnect", {"fields": ("role", "validation_status", "rejection_reason")}),
    )

    list_display = (
        "username",
        "email",
        "role",
        "validation_status",
        "is_staff",
        "is_superuser",
        "is_active",
        "rejection_reason",
    )
    list_filter = ("role", "validation_status", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "phone")
    search_fields = ("user__username", "company_name", "phone")


@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "phone")
    search_fields = ("user__username", "company_name", "phone")