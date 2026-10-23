from django.contrib import admin

from .models import FoundingMember, Notice, OrganizationInformation

admin.site.register(OrganizationInformation)
admin.site.register(Notice)


@admin.register(FoundingMember)
class FoundingMemberAdmin(admin.ModelAdmin):
    exclude = ("image",)
