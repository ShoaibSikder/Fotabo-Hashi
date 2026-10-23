from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "blood_group",
        "is_available_for_donation",
        "self_reported_donation_count",
        "approved_donation_count",
    )
    search_fields = ("name", "user__email", "phone")
