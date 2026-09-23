from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "resource_type", "resource_id", "created_at")
    list_filter = ("action", "resource_type", "created_at")
    search_fields = ("actor__email", "resource_type", "resource_id", "description")
    readonly_fields = ("actor", "action", "resource_type", "resource_id", "description", "ip_address", "user_agent", "metadata", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False