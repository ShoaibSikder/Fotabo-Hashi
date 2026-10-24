from django.contrib import admin

from infrastructure.cache.invalidation import (
    invalidate_founding_members,
    invalidate_organization_content,
    invalidate_public_notices,
)

from .models import FoundingMember, Notice, OrganizationInformation


class CacheInvalidatingAdmin(admin.ModelAdmin):
    cache_invalidator = None

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        self.cache_invalidator()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        self.cache_invalidator()

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        self.cache_invalidator()


@admin.register(OrganizationInformation)
class OrganizationInformationAdmin(CacheInvalidatingAdmin):
    cache_invalidator = staticmethod(invalidate_organization_content)


@admin.register(Notice)
class NoticeAdmin(CacheInvalidatingAdmin):
    cache_invalidator = staticmethod(invalidate_public_notices)


@admin.register(FoundingMember)
class FoundingMemberAdmin(CacheInvalidatingAdmin):
    exclude = ("image",)
    cache_invalidator = staticmethod(invalidate_founding_members)
