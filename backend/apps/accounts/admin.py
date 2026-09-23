from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "role", "is_active", "is_staff", "created_at")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email",)
    readonly_fields = ("created_at", "updated_at", "last_login")

    fieldsets = (
        ("Authentication", {"fields": ("email", "password")}),
        (
            "Authorization",
            {
                "fields": (
                    "role", "is_active", "is_staff", "is_superuser",
                    "groups", "user_permissions",
                )
            },
        ),
        ("Timestamps", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            "User",
            {
                "classes": ("wide",),
                "fields": (
                    "email", "password1", "password2", "role", "is_active", "is_staff",
                ),
            },
        ),
    )