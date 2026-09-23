from django.contrib import admin

from .models import BloodRequest


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ("blood_group", "required_units", "location", "status", "requester", "created_at")
    list_filter = ("status", "blood_group")
    search_fields = ("location", "description", "requester__email")